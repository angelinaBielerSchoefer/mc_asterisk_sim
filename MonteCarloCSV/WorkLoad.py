class WorkLoad:
    def __init__(self, story_point, time_spend):
        self.story_point = story_point
        self.time_spend = time_spend

    def to_dict(self):
        return {
            'story_point': int(self.story_point),
            'time_spend': int(self.time_spend),
        }