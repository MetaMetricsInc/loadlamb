import asyncio

from loadlamb.chalicelib.load import LoadLamb


loop = asyncio.get_event_loop()


def run_handler(event, context):
    return loop.run_until_complete(LoadLamb(event).run())

