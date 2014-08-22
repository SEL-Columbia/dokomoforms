What is validated:
1. Answers match the question type.
2. You cannot answer a question more than once per submission.
3. A question must have a non-empty title.
4. Questions in a survey have unique integer sequence numbers.
5. A question that should have choices associated with it must provide choices.
6. A question that introduces a branch must specify a sequence number for each choice.
7. A sequence number specified for a question must be larger than the sequence number of the question.
8. A user cannot have two surveys with the same name.
What is not:
1. A sequence number specified by a question does not have to exist.
* Reasoning: You can write question 1 knowing that you will want to point to questions 2 and 3 in the future.
2. A choice specified by an answer does not have to exist in the question.
* Reasoning: This would require a view or trigger and is easy to detect/avoid in the application.
3. Answer types irrelevant to the question do not have to be NULL.
* Reasoning: This would make the constraints huge, and on the application side you can just ignore the irrelevant columns.

