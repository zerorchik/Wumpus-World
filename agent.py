import numpy as np
import collections

"""
Містить визначення агента, який буде працювати в середовищі.
"""

ACT_UP = 1
ACT_DOWN = 2
ACT_LEFT = 3
ACT_RIGHT = 4
ACT_TORCH_UP = 5
ACT_TORCH_DOWN = 6
ACT_TORCH_LEFT = 7
ACT_TORCH_RIGHT = 8


class RandomAgent:
    def __init__(self):
        """
        Ініціалізує агента з параметрами навчання.
        """
        self.learning_rate = .01  # Швидкість навчання
        self.gamma = .8

        self.epsilon_a = -1 / 900
        self.epsilon_b = 1

        # Функція стан-дія (Q-функція)
        self.q_table = {}

        # Епізод визначається як кожний раз, коли ми починаємо рухатися до тих пір, поки не помремо
        self.n_episode = 0

        # Крок визначається як ітерація в кожній грі
        self.step = 0

        self.cumul_reward = 0

    def reset(self):
        """
        Скидає параметри агента для нового епізоду.
        """
        self.step = 0
        self.n_episode += 1
        if self.n_episode == 1000:
            print(self.cumul_reward)
            # print(self.q_table)

    def act(self, observation):
        """
        Вибирає дію на основі спостережень.
        """
        self.step += 1
        self.epsilon = 0.5

        position, smell, breeze, charges = observation

        self.create_state(observation)
        state_action = self.q_table[observation]

        if self.n_episode >= 900:
            if smell and charges > 0:
                # Вибирає найкращу дію для стратегії експлуатації
                return self.choose_action(state_action)
            else:
                # Вибирає найкращу дію для стратегії експлуатації
                return self.choose_action(state_action[0:4])

        # Вибирає найкращу дію для стратегії експлуатації
        if smell and charges > 0:
            return self.choose_action(state_action)
        else:
            return self.choose_action(state_action[0:4])

    def reward(self, observation, action, reward):
        """
        Отримує винагороду після виконання дії.
        """
        if self.step > 1:
            self.learn(s=observation,
                       a=action - 1,
                       r=reward,
                       s_=self.next_observation(observation, action),
                       )
        if self.n_episode >= 900:
            self.cumul_reward += reward

    def create_state(self, state):
        """
        Якщо новий стан, створіть його в q_table, зі значеннями за замовчуванням = 0.
        """
        if state not in self.q_table.keys():
            self.q_table[state] = 8 * [10]

    def learn(self, s, a, r, s_):
        """
        Оновлює Q-функцію на основі отриманих винагород.
        """
        self.create_state(s_)  # Створює тільки якщо не існує
        q_predict = self.q_table[s][a]
        q_target = r + self.gamma * max(self.q_table[s_])
        self.q_table[s][a] += self.learning_rate * (q_target - q_predict)

    def choose_action(self, state_action):
        """
        Вибирає дію на основі значень Q-функції.
        """
        # Отримання списку дій з максимальним значенням в таблиці Q
        action_with_max_value = [i for i in range(len(state_action)) if state_action[i] == max(state_action)]
        return np.random.choice(action_with_max_value) + 1

    def next_observation(self, observation, action):
        """
        Повертає нове спостереження після виконання дії.
        """
        position, smell, breeze, charges = observation
        if action >= 4 and charges > 0:
            charges -= 1
            next_observation = (self.next_position(position, action), smell, breeze, charges)
        else:
            next_observation = (self.next_position(position, action), smell, breeze, charges)

        return next_observation

    def next_position(self, position, action):
        """
        Обчислює нове положення після виконання дії.
        """
        x, y = position
        if action == 1 and y <= 2:
            y += 1
        elif action == 2 and y >= 1:
            y -= 1
        elif action == 3 and x >= 1:
            x -= 1
        elif action == 4 and x <= 2:
            x += 1
        return x, y


Agent = RandomAgent