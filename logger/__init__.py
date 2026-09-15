from logging import getLogger, addLevelName, INFO, DEBUG, ERROR, NOTSET, StreamHandler, FileHandler
from sys import stdout, stderr

LOGGER = getLogger("pySAP")
TRACE  = 1

addLevelName(TRACE,"TRACE")

LOGGER.setLevel(INFO)

handlers = {
    'stdout': {
        'type'   : 'stream',
        'target' : stdout,
        'level'  : DEBUG,
    },
    'stderr': {
        'type'   : 'stream',
        'target' : stderr,
        'level'  : ERROR,
    },
    'applog': {
        'type'   : 'file',
        'target' : 'pySAP_trace.log',
        'level'  : NOTSET,
    },
}
for destination in handlers:
    config = handlers[destination]
    if config['type'] == 'stream':
        config['handler'] = StreamHandler(stream=config['target'])
    elif config['type'] == 'file':
        config['handler'] = FileHandler(config['target'])
    config['handler'].setLevel(config['level'])
    LOGGER.addHandler(config['handler'])
