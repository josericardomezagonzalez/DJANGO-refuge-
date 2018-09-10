class LiveDataConsumer {

    constructor(options, actions) {
        this.options = options;
        this.actions = actions;
        this.init(this.auth_msg_data, this.connection_str);
        this.start_listener();
        this.event_to_close_websocket(this.socket);
    }

    init(auth_msg_data, connection_str) {
        let data = {
            type: 'auth_msg',
            data: auth_msg_data,
        };
        let data_str = JSON.stringify(data);
        let socket = new WebSocket(connection_str);
        socket.addEventListener('open', (event) => {
            socket.send(data_str);
        });
        this.socket = socket;

    }
    
    event_to_close_websocket(socket) {
        let data = {
            type: 'close_web_socket',
            data: { token: this.options.token },
        };
        document.onreadystatechange = function (){
            window.onunload = function() {
                socket.send(JSON.stringify(data));
            }
        }
    }

    start_listener() {
        this.socket.addEventListener('message', (event) => {
            let data_json = JSON.parse(event.data);
            this.actions[data_json.type](data_json.data);
        });

    }

    change_variables(variables) {

        this.update_variables_local(variables);
        let data = {
            type: 'change_variables',
            data: this.auth_msg_data,
        };
        this.send(data);
        console.log(data);
    }

    send(message) {
        message = JSON.stringify(message);
        this.socket.send(message);

    }

    get connection_str() {
        return this.options.host + ':' + this.options.port;
    }

    update_variables_local(variables_new) {
        for (let key in variables_new) {
            this.options[key] = variables_new[key];
        }
    }

    get variables() {
        return {
            user_id: this.options.user_id,
            token: this.options.token,
            campaign_id: this.options.campaign_id
        };
    }

    get auth_msg_data() {
        return {
            user_id: this.options.user_id,
            token: this.options.token,
            variables: this.variables,
            actions: Object.keys(this.actions)
        };
    }


}