import anyio


async def main():
    start = anyio.current_time()
    async with anyio.create_task_group():
        
        with anyio.move_on_after(1) as scope:
            print('Starting sleep')
            await anyio.sleep(2)
            print('This should never be printed')
            
        # The cancel_called property will be True if timeout was reached
        print('Exited cancel scope, cancelled =', scope.cancel_called)
            
        with anyio.move_on_after(3) as scope:
            print('Starting sleep')
            await anyio.sleep(2)
            print('This should be printed')

        # The cancel_called property will be True if timeout was reached
        print('Exited cancel scope, cancelled =', scope.cancel_called)
        
    runtime = anyio.current_time() - start
    print(f'program executed in {runtime:.2f}s')

anyio.run(main)
