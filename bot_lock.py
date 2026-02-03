import os
import time
import logging

logger = logging.getLogger(__name__)

class BotLock:
    def __init__(self, lock_file='bot.lock'):
        self.lock_file = lock_file
        self.pid = os.getpid()
    
    def acquire(self):
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                
                try:
                    os.kill(old_pid, 0)
                    logger.warning(f'Bot ya está ejecutándose con PID {old_pid}')
                    return False
                except OSError:
                    logger.info(f'Proceso anterior {old_pid} no existe, limpiando lock')
                    os.remove(self.lock_file)
            except Exception as e:
                logger.error(f'Error verificando lock: {e}')
                os.remove(self.lock_file)
        
        with open(self.lock_file, 'w') as f:
            f.write(str(self.pid))
        
        logger.info(f'Lock adquirido con PID {self.pid}')
        return True
    
    def release(self):
        try:
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
                logger.info(f'Lock liberado para PID {self.pid}')
        except Exception as e:
            logger.error(f'Error liberando lock: {e}')
