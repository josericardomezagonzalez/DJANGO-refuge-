import json
from django.conf import settings

connection = settings.AMQP_CONECTION


def publish(routing_key, message):
    channel = connection.channel()
    channel.exchange_declare(exchange='topic_logs',
                             exchange_type='topic')
    channel.basic_publish(exchange='topic_logs',
                          routing_key=routing_key,
                          body=json.dumps(message))
    print(" [x] Sent %r:%r" % (routing_key, json.dumps(message)))
    # si existe un token origen crea una nueva publicacion de redireccion
