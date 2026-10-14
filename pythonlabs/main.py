import tasks.task1 as task1
import tasks.task2 as task2
import tasks.task3 as task3

i = input("Выбрать задачу(1, 2, 3): ")

match i:
    case "1":
        print("=" * 70)
        print("ЗАДАЧА 1: Численное решение методом Эйлера")
        print("=" * 70)

        task1.start()

    case "2":
        print("\n" + "="*70)
        print("ЗАДАЧА 2: Исследование погрешности во времени")
        print("="*70)

        task2.start()

    case "3":
        print("\n" + "="*70)
        print("ЗАДАЧА 3: Зависимость ошибки от шага")
        print("="*70)

        task3.start()

    case _:
        print("Некорректный ввод")
