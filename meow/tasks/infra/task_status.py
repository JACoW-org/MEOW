
class TaskStatus:
    """ """

    running_tasks = list()
    
    @classmethod
    def print(cls) -> None:
        print(cls.running_tasks)
    
    @classmethod
    def is_running(cls, task_id: str) -> bool:
        return task_id in cls.running_tasks
    
    @classmethod
    def start_task(cls, task_id: str) -> None:
        cls.running_tasks.append(task_id)
    
    @classmethod
    def stop_task(cls, task_id: str) -> None:
        if cls.is_running(task_id=task_id):
            cls.running_tasks.remove(task_id)
    