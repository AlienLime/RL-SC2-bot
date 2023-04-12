import asyncio
import aiohttp
import gymnasium as gym
# from codetiming import Timer

async def task(name, work_queue):
    # timer = Timer(text=f"Task {name} elapsed time: {{:.1f}}")
    async with aiohttp.ClientSession() as session:
        while not work_queue.empty():
            url = await work_queue.get()
            print(f"Task {name} getting URL: {url}")
            # timer.start()
            async with session.get(url) as response:
                await response.text()
            # print("work_wur", work_queue.qsize())
            # timer.stop()

async def main(work_queue):
    """
    This is the main entry point for the program
    """

    while True:
        # Put some work in the queue
        print("while True")
        for url in [
            "http://google.com",
            "http://yahoo.com",]:
            await work_queue.put(url)
        print("put all urls")
        # Run the tasks
        # with Timer(text="\nTotal elapsed time: {:.1f}"):
        await asyncio.gather(
            asyncio.create_task(task("One", work_queue)),
            asyncio.create_task(task("Two", work_queue)),
        )
        print("gathered all")


from threading import Thread

class AST(Thread):
    # PuppetThread()
    def __init__(self):
        self.work_queue = asyncio.Queue()
        # setup result_queue_out
        
        # setup action_queue_in
        # Setup SC2Bot()

        super().__init__()


    def run(self) -> None:
        asyncio.run(main(self.work_queue))

    def join() -> None:
        pass

if __name__ == "__main__":
    # Create the queue of work
    t = AST()
    t.start()
    async def addtv2(url="http://tv2.dk"):
        t.value = url
        await t.work_queue.put(url)
    asyncio.run(addtv2("http://dr.dk"))

    bb = 234
    class SC2Env(gym.env):
        
        def reset(self):
            self.pcom = AST()

        def step(self, a):
            async def add_an_action(action):
                await self.pcom.action_in_queue.put(action)
            # Husk at checke om koerne er sat op.
            asyncio.run(add_an_action(a))

            async def get_an_action(action):
                # check out-køen i et while-loop. Når den har et element, returnerer det.
                 result = await self.pcom.result_queue_out.get()
                 SC2Env.value = result.value()

            value = asyncio.run(get_an_action(a)) # who knows..

    s = [addtv2() for _ in range(10)]
    asyncio.run(addtv2("http://dr.dk"))



    # work_queue("")


    a = 234