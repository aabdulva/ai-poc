from typing import Optional

from ollama import chat
from pydantic import BaseModel


MODEL_NAME = "llama3.2"


class TestAnalysis(BaseModel):
    component: Optional[str]
    error_codes: list[str]
    symptoms: list[str]
    operating_condition: Optional[str]
    software_version: Optional[str]


class TestLogAnalyzer:

    def __init__(self):
        self.model = MODEL_NAME

    def analyze(self, test_log: str) -> TestAnalysis:

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """
You are an automotive software test failure analysis assistant.

Analyze the provided test log and extract all technically
relevant information that could help identify a previously
reported failure.

Rules:

1. Extract ALL distinct symptoms explicitly stated in the log.

2. Do not summarize multiple symptoms into one symptom if
   they are technically different.

3. Preserve important technical wording.

4. Extract exact error codes exactly as they appear.

5. Extract the component exactly as identified.

6. Extract the operating condition or state.

7. Extract software versions if explicitly present.

8. Do not invent information.

For example, if the log contains:

"Camera service failed to initialize.
CAN communication timeout.
Retry count exceeded."

return three separate symptoms:

- Camera service failed to initialize
- CAN communication timeout
- Retry count exceeded
"""
                },
                {
                    "role": "user",
                    "content": test_log
                }
            ],
            format=TestAnalysis.model_json_schema(),
            options={
                "temperature": 0
            }
        )

        return TestAnalysis.model_validate_json(
            response.message.content
        )


def main():

    test_log = """
    ECU: CAM
    Component: CameraService
    State: WAKEUP

    ERROR CAM_1032

    Camera service failed to initialize.
    CAN communication timeout.
    Retry count exceeded.
    """

    analyzer = TestLogAnalyzer()

    result = analyzer.analyze(test_log)

    print()
    print("======================================")
    print("LLM Test Log Analysis")
    print("======================================")
    print()

    print(f"Component:          {result.component}")
    print(f"Error codes:        {result.error_codes}")
    print(f"Symptoms:           {result.symptoms}")
    print(f"Operating condition:{result.operating_condition}")
    print(f"Software version:   {result.software_version}")


if __name__ == "__main__":
    main()