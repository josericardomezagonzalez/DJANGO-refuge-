#!/usr/bin/env node

let port = parseInt(process.argv[2]);
const WebSocket = require('ws');
let amqp = require('amqplib/callback_api'); // message consumer
let request = require('request-promise'); // web service 
let sockets = new Map();
let amqp_conn;
const web_socket_server = new WebSocket.Server({ port: port });
const ROUTING_KEY = {
    confirm_new_session_token: ['*', 'user_id', '*'],
    close_message_confirm: ['token', '#', 'campaign_id', '#'],
    success_session_redirect: ['token', 'campaign_id', 'user_id'],
    instance_creationevent: ['token'],
    campaign_request: ['campaign_id'],
    conversion: ['user_id'],
    offer_click: ['campaign_id']
};
const AUTHENTICATION_URL = 'http://localhost:8000/user/session/token/auth.json';

let ws_actions = {
    auth_msg: (data, web_socket) => {
        request_authentication_user_socket(data, web_socket);
    },
    change_variables: (data, web_socket) => {
        valid_change_variables_user(data, web_socket);
    },
    close_web_socket: (data, web_socket) => {
        let token = data.token;
        let data_user = sockets.get(token);
        data_user.web_socket.close();
        data_user.channel.close();
        sockets.delete(token);
        console.log("closed socket (token) :"+ token);
    }
};

let amqp_actions = {
    send_web_socket_client: (data, token, action) => {
        // cierra el canal amqp si el servidor de django lo solicito
        let data_user = sockets.get(token);
        let message = {
            type: action,
            data: data
        };
        let socket = data_user.web_socket;
        if (socket.readyState === socket.OPEN) {
            socket.send(JSON.stringify(message), action);
        }
    }
};

web_socket_server.on('connection', (web_socket) => {

    web_socket.on('message', (message) => {
        let data_json = JSON.parse(message);
        ws_actions[data_json.type](data_json.data, web_socket);
    });
    web_socket.on('error', (err) => {
        console.log('server socket error: ' + err);
    });

});

amqp.connect('amqp://localhost', (err, conn) => {
    amqp_conn = conn;
});


async function valid_change_variables_user(data, web_socket) {
    let token = data.token;
    let data_user = sockets.get(token);
    let channel = data_user.channel;
    let valid = await request_authentication_user_socket(data, web_socket);
    if (valid) {        
        channel.close();
    }

};


async function request_authentication_user_socket(data, web_socket) {
    let { token, user_id, variables, actions } = data;
    let options = {
        uri: AUTHENTICATION_URL,
        qs: {
            user_id: user_id,
            token: token,
            variables: variables
        },
        headers: {
            'User-Agent': 'Request-Promise'
        },
        json: true
    };
    try {
        let response = await request(options);
        let valid = response.valid;
        if (!valid) {
            web_socket.close();
            return false;
        }
        let routing_keys_map = generate_routing_key_for_user(actions, variables);
        sockets.set(token, {
            user_id: user_id,
            web_socket: web_socket,
            routing_keys_map: routing_keys_map
        });
        generate_amqp_channels(Object.keys(routing_keys_map), token);
        console.log(new Date() + 'conneccion new (token): ' + token);
        return true;
    } catch (err) {
        console.log(err);
    }
};


function generate_routing_key_for_user(actions, variables) {
    let routing_keys_map = {};
    for (let route of actions) {
        let key_value_acumu = '';
        let key = ROUTING_KEY[route];
        for (let key_v of key) {
            if (key_v == '*' || key_v == '#') {
                key_value_acumu += '.' + key_v;
                continue;
            }
            let key_value = variables[key_v];
            if (!key_value) {
                throw Exception("value in action " + route + " not allowed: " +
                      key_v);
            }
            key_value_acumu += '.' + key_value;
        }
        routing_keys_map[route + key_value_acumu] = route;
    }
    return routing_keys_map;
}

async function generate_amqp_channels(routing_keys, token) {

    let channel = await create_amqp_channel();
    let ex = 'topic_logs';
    channel.assertExchange(ex, 'topic', { durable: false });
    //durable true sobrevive a los reinicios del intermediario
    let new_queue = await assert_queue(channel, '', { exclusive: true });
    routing_keys.forEach(function(key) {
        channel.bindQueue(new_queue.queue, ex, key);
    });
    let data_user = sockets.get(token);
    data_user.channel = channel;
    sockets.set(token, data_user);
    channel.consume(new_queue.queue, generate_amqp_message_consumer(token),
                                                          { noAck: true });
}


function generate_amqp_message_consumer(token) {
    return function(msg) {
        let data = JSON.parse(msg.content.toString());
        let msg_routing = msg.fields.routingKey;
        let routing_keys_map = sockets.get(token).routing_keys_map;
        let action = routing_keys_map[msg.fields.routingKey];
        amqp_actions.send_web_socket_client(data, token, action);
        console.log(new Date() + ' [amqp says] %s: %s',
            msg.fields.routingKey,
            msg.content.toString());
    }
}

function create_amqp_channel() {
    return new Promise(function(resolve, reject) {
        amqp_conn.createChannel((err, ch) => {
            if (err) {
                reject(err);
            } else {
                resolve(ch);
            }
        });
    });
}

function assert_queue(ch, q_name, q_options) {
    return new Promise(function(resolve, reject) {
        ch.assertQueue(q_name, q_options, (err, q) => {
            if (err) {
                reject(err);
            } else {
                resolve(q);
            }
        });
    });
}

function Exception(message) {
    this.message = message;
}