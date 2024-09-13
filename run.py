from app import create_app
import logging

# Set up logging
logging.basicConfig(
    filename='/app/logs/app.log',  # Log file location
    level=logging.DEBUG,           # Log level
    format='%(asctime)s %(levelname)s %(message)s',  # Log format
)

# Example usage of logging
logging.info('Starting application...')
logging.debug('Debugging information...')
logging.error('An error occurred')

app = create_app()

if __name__ == "__main__":
    app.run()
