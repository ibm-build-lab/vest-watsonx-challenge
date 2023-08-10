# _watsonx.ai_ Service

This documents briefly highlights the _watsonx.ai_ service within the vest-watsonx-challenge repo.

This services interfaces with _watsonx.ai_ through REST API calls by taking in user provided input, setting some tuning parameters (customizable), and returning a generated text responses.

The list of paramentes is listed below, but please note a few limitations that are required to make use of this services are also listed below.

### Limitations 
- Currently the API only supports the "google/flan-ul2" LLM _(limitation from watsonx.ai REST API)_
- Queries to _watsonx.ai_ requires an API Key in order to receive a response
- Queries to _watsonx.ai_ also require a projectId in order to receive a response

## Foundation Model Tuning Parameters

The following table showcase the list of some of the parameters that can be used to help tune queries to _watsonx.ai_ from our own internal `/watsonx/query` API.
Most of these parameters are optional and the defaults are used if any are found missing during a query.

| MetaName              | Type  | Required | Schema                                                                                                                                    | Range of Value                                |
| --------------------- | ----- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| DECODING_METHOD       | str   | N        | sample                                                                                                                                    | Greedy or Sample                              |
| LENGTH_PENALTY        | dict  | N        | {'decay_factor': 2.5, 'start_index': 5}                                                                                                   | -                                             |
| TEMPERATURE           | float | N        | 0.5                                                                                                                                       | 0 to 2.0                                      |
| TOP_P                 | float | N        | 0.2                                                                                                                                       | 0 to 1.0                                      |
| TOP_K                 | int   | N        | 1                                                                                                                                         | 1 to 100                                      |
| RANDOM_SEED           | int   | N        | 33                                                                                                                                        | 1 to 4,294,967,295                            |
| REPETITION_PENALTY    | float | N        | 2                                                                                                                                         | 1.0 to 2.0                                    |
| MIN_NEW_TOKENS        | int   | N        | 50                                                                                                                                        | 1 to 1024                                     |
| MAX_NEW_TOKENS        | int   | N        | 200                                                                                                                                       | 1 to 1024                                     |
| STOP_SEQUENCES        | list  | N        | ['fail']                                                                                                                                  | 0 to 6 strings, each no longer than 40 tokens |
| TIME_LIMIT            | int   | N        | 600000                                                                                                                                    | -                                             |
| TRUNCATE_INPUT_TOKENS | int   | N        | 200                                                                                                                                       | -                                             |
| RETURN_OPTIONS        | dict  | N        | {'input_text': True, 'generated_tokens': True, 'input_tokens': True, 'token_logprobs': True, 'token_ranks': False, 'top_n_tokens': False} | _                                             |
