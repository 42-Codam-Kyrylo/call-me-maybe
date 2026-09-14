
# from llm_sdk import Small_LLM_Model

# def main():
#     print("Загрузка модели...")
#     model = Small_LLM_Model()

#     prompt = "The capital of France is"
#     print(f"Промпт: {prompt}\n")

#     # 1. Превращаем текст в токены (числа)
#     # encode возвращает тензор, поэтому берем список чисел с помощью .squeeze().tolist()
#     tokens = model.encode(prompt).squeeze().tolist()

#     # Мы сгенерируем ровно 10 новых токенов
#     max_new_tokens = 10

#     print("Генерируем ответ:", end=" ", flush=True)

#     for _ in range(max_new_tokens):
#         # 2. Получаем "логиты" (сырые оценки вероятностей) для следующего слова
#         # get_logits_from_input_ids принимает список токенов и возвращает список чисел (логитов)
#         logits = model.get_logits_from_input_ids(tokens)

#         # 3. Находим индекс самого вероятного токена (то есть максимальное число в списке logits)
#         # Встроенная функция max с параметром key поможет найти индекс наибольшего элемента
#         next_token = max(range(len(logits)), key=lambda i: logits[i])

#         # 4. Добавляем новый токен к нашей последовательности
#         tokens.append(next_token)

#         # Печатаем только что сгенерированный токен, чтобы видеть результат в реальном времени
#         # Декодируем список из одного токена обратно в текст
#         print(model.decode([next_token]), end="", flush=True)

#     print("\n\nГотово! Полный текст:")

#     # 5. В конце декодируем всю последовательность целиком
#     full_text = model.decode(tokens)
#     print(full_text)

# if __name__ == "__main__":
#     main()

# import numpy as np
# from llm_sdk import Small_LLM_Model


# def main():
#     print("Загрузка модели...")
#     model = Small_LLM_Model()

#     prompt = "The capital of France is"
#     print(f"Промпт: {prompt}\n")

#     # 1. Получаем базовый список токенов [int, int, ...]
#     tokens = model.encode(prompt).tolist()[0]

#     max_new_tokens = 10
#     print("Генерируем ответ:", end=" ", flush=True)

#     for _ in range(max_new_tokens):
#         # 2. Получаем логиты. Метод принимает list[int] и возвращает list[float]
#         logits = model.get_logits_from_input_ids(tokens)

#         # 3. Используем разрешенный numpy для поиска индекса максимального числа
#         next_token = int(np.argmax(logits))

#         # 4. Добавляем токен
#         tokens.append(next_token)

#         # Печатаем шаг за шагом (decode тоже принимает список)
#         print(model.decode([next_token]), end="", flush=True)

#     print("\n\nГотово! Полный текст:")
#     full_text = model.decode(tokens)
#     print(full_text)


# if __name__ == "__main__":
#     main()