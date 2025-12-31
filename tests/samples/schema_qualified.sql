create table "my_schema"."table_x" (id int);
create table public."table_y" (id int references "my_schema"."table_x");
create table `another_schema`.`table_z` (id int references public.`table_y`);
