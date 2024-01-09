"""
Це обладнання, яке запускає вашого агента в середовищі.
"""

class Runner:
    def __init__(self, environment, agent, verbose=False):
        self.environment = environment
        self.agent = agent
        self.verbose = verbose

    def step(self):
        """
        Виконує один крок взаємодії агента з середовищем.
        """
        observation = self.environment.observe()
        action = self.agent.act(observation)
        (reward, stop) = self.environment.act(action)
        self.agent.reward(observation, action, reward)
        return (observation, action, reward, stop)

    def loop(self, games, max_iter):
        """
        Запускає серію ігор та ітерацій для агента в середовищі.
        """
        cumul_reward = 0.0
        for g in range(1, games+1):
            self.agent.reset()
            self.environment.reset()
            for i in range(1, max_iter+1):
                if self.verbose:
                    print("Simulation step {}:".format(i))
                    self.environment.display()
                (obs, act, rew, stop) = self.step()
                cumul_reward += rew
                if self.verbose:
                    print(" ->       observation: {}".format(obs))
                    print(" ->            action: {}".format(act))
                    print(" ->            reward: {}".format(rew))
                    print(" -> cumulative reward: {}".format(cumul_reward))
                    if stop is not None:
                        print(" ->    Terminal event: {}".format(stop))
                    print()
                if stop is not None:
                    break
            if self.verbose:
                print(" <=> Finished game number: {} <=>".format(g))
                print()
        return cumul_reward

def iter_or_loopcall(o, count):
    """
    Перевіряє, чи об'єкт можна викликати, і в іншому випадку повертає ітератор або виклик функції.
    """
    if callable(o):
        return [ o() for _ in range(count) ]
    else:
        # Повинен бути ітерований
        return list(iter(o))

class BatchRunner:
    """
    Запускає кілька екземплярів того самого завдання RL паралельно
    і агрегує результати.
    """

    def __init__(self, env_maker, agent_maker, count, verbose=False):
        self.environments = iter_or_loopcall(env_maker, count)
        self.agents = iter_or_loopcall(agent_maker, count)
        assert(len(self.agents) == len(self.environments))
        self.verbose = verbose
        self.ended = [ False for _ in self.environments ]

    def game(self, max_iter):
        """
        Запускає одну гру для кожного агента та середовища та повертає середню винагороду.
        """
        rewards = []
        for (agent, env) in zip(self.agents, self.environments):
            agent.reset()
            env.reset()
            game_reward = 0
            for i in range(1, max_iter+1):
                observation = env.observe()
                action = agent.act(observation)
                (reward, stop) = env.act(action)
                agent.reward(observation, action, reward)
                game_reward += reward
                if stop is not None:
                    break
            rewards.append(game_reward)
        return sum(rewards)/len(rewards)

    def loop(self, games, max_iter):
        """
        Запускає серію ігор для всіх агентів та середовищ і повертає кумулятивну середню винагороду.
        """
        cum_avg_reward = 0.0
        total_avg_reward = 0.0  # Змінна для зберігання суми середніх reward за кожну гру
        for g in range(1, games + 1):
            avg_reward = self.game(max_iter)
            total_avg_reward += avg_reward  # Додаємо середній reward до загальної суми
            cum_avg_reward = total_avg_reward / g  # Обчислюємо кумулятивний середній reward
            if self.verbose:
                print("Simulation game {}:".format(g))
                print(" ->            average reward: {}".format(avg_reward))
                print(" -> cumulative average reward: {}".format(cum_avg_reward))
        return cum_avg_reward