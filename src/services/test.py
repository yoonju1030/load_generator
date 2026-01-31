class TestService():
    def __init__(self):
        pass

    def make_result(self):
        try:
            return {"msg": "success"}
        except Exception as e:
            raise e