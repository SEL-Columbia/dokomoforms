
```sql
doko=# select survey_id from survey;
              survey_id               
--------------------------------------
 8b1d023e-b716-4075-bff6-b0aa06d44a18
 
doko=# select question_id, sequence_number, title, type_constraint_name, allow_multiple from question order by sequence_number;
             question_id              | sequence_number |                                                                                      title                                                                                      | type_constraint_name | allow_multiple 
--------------------------------------+-----------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------+----------------
 147a09b1-1148-4161-b2d1-0514c1e6ee67 |               1 | Is this facility on your facility list?                                                                                                                                        | multiple_choice      | f
 4e8451a6-d8b9-4942-9193-ab411ccf154e |               2 | Please enter the UID exactly as it appears on your facility list.                                                                                                               | text                 | f
 8618fd08-f809-42f1-b1cd-715a8fa1d94a |               3 | Facility Type - pick one of the following that best describes this facility.                                                                                                  | multiple_choice      | f
 27cf92b0-ed68-4824-9639-b57c3633a6e4 |               4 | How many doctors are posted full-time at this facility?                                                                                                                         | integer              | f
 412549d6-7442-48a0-a04a-8842777a58ce |               5 | How many midwives and nurse-midwives are posted full-time at this facility?                                                                                                     | integer              | f
 0a3e8319-8c83-4d7d-935e-d96535724c5c |               6 | How many nurses (who are not nurse-midwives) are posted full-time at this facility?                                                                                             | integer              | f
 93ca6b91-582a-4618-ab42-0a673e895256 |               7 | How many CHEWs and JCHEWs (community health extension workers) are posted full-time at this facility?                                                                           | integer              | f
 677d8ddd-b020-499d-87fc-af9249f2fed9 |               8 | Is there an emergency transport vehicle (motorized vehicle, tricycle, or engine boat) available at this facility? Motorcycles and canoes do not count.                          | multiple_choice      | f
 6d1a4669-4112-45e6-b3e5-f5e17f90414e |               9 | Is there an emergency transport vehicle (motorized vehicle, tricycle, or engine boat) that can be called and will arive within 30 minutes? Motorcycles and canoes do not count. | multiple_choice      | f
 c7ccf587-1132-4a39-ba49-6d07136e557c |              10 | Does this facility have a refrigerator or freezer for vaccine storage?                                                                                                          | multiple_choice      | f
 936d1a8c-0823-4ba3-af36-f7eb5f722ee5 |              11 | Does this facility have a portable vaccine carrier or cold box for the transport of vaccines?                                                                                   | multiple_choice      | f
 fc0c59ab-10d2-45d7-a8db-c72daa411959 |              12 | What type(s) of power sources are available and functional at this facility?                                                                                                    | multiple_choice      | t
 fef61679-1652-4414-afb2-ac180a9fa68c |              13 | Which of the following IMPROVED sanitation facilities are on the premises?                                                                                                      | multiple_choice      | t
 791bc15b-daf9-4cc1-8842-5be6195cb836 |              14 | Which of the following IMPROVED water points are used by the facility and located within 100 meters of the facility?                                                            | multiple_choice      | t
 06665066-0abe-4797-82f2-73bd28be866b |              15 | How many rooms are in this facility?                                                                                                                                            | integer              | f
 e1fe3ece-7eec-494d-aee4-d4025514c654 |              16 | How many beds are in this facility?                                                                                                                                             | integer              | f
```
