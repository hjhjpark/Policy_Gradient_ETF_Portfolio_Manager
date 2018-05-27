import numpy as np

class Environment:

    def __init__(self, chart_df, feature_df, window_size=30):
        self.chart_df = chart_df
        self.feature_df = feature_df
        self.init_money = 10000000
        self.window_size = window_size
        self.idx = window_size - 1

        self.prev_pv = self.init_money
        self.prev_action = None
        self.prev_observation = None

    def reset(self):
        self.idx = self.window_size - 1
        observation = self.feature_df.iloc[0:self.idx + 1]
        self.curr_pv = self.init_money

        return observation

    def step(self, action):
        """

        :param action: 포트폴리오 벡터 e.g [0.1, 0.1, ...]

        :return: observation, reward, done
        observation는 현재 환경의 상태. 즉, 현재 가격정보(트레이닝에 사용하는) 주면 됨.
        reward는 현재 포트폴리오 가치, 또는 sharp ratio 같은 것들을 주면 됨
        done은 해당 기간 데이터 전부 소진하였는지 여부
        """

        done = False
        self.idx += 1

        action = self._validate_action(action)
        reward = self.calc_PV(action)
        self.prev_action = action

        observation = self.feature_df.iloc[self.idx+1-self.window_size : self.idx+1]

        if self.idx + 1 >= len(self.feature_df):
            done = True

        return observation, reward, done

    def calc_PV(self, action):
        """
        :param action:
        :param observation:
        :return: 포트폴리오 밸류를 리턴한다. 단위 : 원화
        """

        price0_arr = self.feature_df.iloc[self.idx-1][:, 'close'].values
        price_arr = self.feature_df.iloc[self.idx][:, 'close'].values
        # print(price_arr)
        pv = sum(price_arr / price0_arr * action * self.prev_pv)

        # 다음 step에 사용하기 위해 self.prev_pv에 저장
        self.prev_pv = pv

        return pv


    def action_sample(self):
        """
        :return: random 한 포트폴리오 벡터를 반환한다. random action으로 볼 수 있다.
        """
        n_asset = len(self.feature_df.columns.levels[0])
        action = np.random.rand(n_asset)
        action /= sum(action)
        return action

    @staticmethod
    def _validate_action(action):
        """
        :param action: action(포트폴리오 벡터)의 합이 1인지 확인하여,
        1이 아닌 경우, normalize 한다.
        :return:
        """
        epsilon = 1e-6
        if sum(action) < 1 - epsilon or sum(action) > 1 + epsilon:
            print("Portfolio Vector(action)의 합이 1이 아닙니다.")
            print("자동으로 비율을 조절합니다.")
            print("before adj:", action)
            action /= sum(action)
            print("after  adj:", action)

        return action