def calculate_runtime(func):
    def wrapper(*args, **kwargs):
        import datetime

        time_start = datetime.datetime.now()
        result = func(*args, **kwargs)
        time_finish = datetime.datetime.now()

        time_delta = time_finish - time_start
        print('- [{func_name}] fonksiyonu {seconds} milisaniye sürdü.'.format(
            func_name=func.__name__,
            seconds=time_delta.microseconds / 1000 / 1000,
        ))

        return result

    return wrapper
