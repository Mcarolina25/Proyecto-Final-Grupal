drop table sitios;

create table sitios(
	gmap_id varchar(80) primary key,
	category text,
	name text,
	address text,
	descripcion varchar(100) ,
	latitude varchar(20),
	longitude varchar(20),
	avg_rating float,
	num_of_reviews numeric,
	price float,
	hours text,
	"MISC" text,
	state varchar(50),
	relative_results text,
	URL text,
	description text
);

select * from sitios 
where upper(category) like '%RES%';
and upper(name) like '%ACME%';


select num_of_reviews, count(num_of_reviews) from sitios
group by num_of_reviews;
select sitios.num_of_reviews , count(*)  from sitios 
group by sitios.num_of_reviews
order by 1 asc
;

--state

drop table business;
create table business(
	business_id varchar(30) primary key,
	name text,
	address text,
	city varchar(60),
	state varchar(5),
	postal_code varchar(10),
	latitude varchar(20),
	longitude varchar(20),
	stars float,
	review_count smallint,
	is_open smallint,
	attributes text,
	categories text,
	hours text,	
    FOREIGN KEY (state, city) REFERENCES target_city (state, city)
);

select * from business;


drop table user_yelp;
create table user_yelp(
	user_id varchar(30) primary key,
	name varchar(50),
	review_count smallint,
	yelping_since date,
	useful numeric,
	funny numeric,
	cool numeric,
	elite text,
	friends text,	
	fans smallint,
	average_stars float,
	compliment_hot smallint,
	compliment_more smallint,
	compliment_profile smallint,
	compliment_cute numeric,
	compliment_list numeric,
	compliment_note numeric,
	compliment_plain numeric,
	compliment_cool numeric,
	compliment_funny numeric,
	compliment_writer numeric,
	compliment_photos numeric
);

select * from user_yelp;

drop table estados;
create table estados(
	estados_id serial primary key,
	user_id varchar(30),
	gmap_id varchar(50),
	name varchar(60),
	time  text,
	rating smallint,
	text text,
	pics json,
	resp json,
	FOREIGN KEY (user_id) REFERENCES user_yelp,
	FOREIGN KEY (gmap_id) REFERENCES sitios
);

select * from estados;

ALTER TABLE business 
ADD PRIMARY KEY (business_id); 

drop table review;
create table review(
	review_id varchar(30) primary key,
	stars smallint,
	date date,
	text_review text,
	useful smallint,
	funny smallint,
	cool smallint,
	text text,
	user_id varchar(30),
	business_id varchar(30) ,
	FOREIGN KEY (user_id) REFERENCES user_yelp ,
	FOREIGN KEY (business_id) REFERENCES business	
);



select * from business
;

drop table checkin;
create table checkin(
	checkin_id serial primary key,
	date text,
	business_id varchar(30),
	FOREIGN KEY (business_id) REFERENCES business	
);

select * from checkin;

drop table tip;
create table tip(
	tip_id serial primary key,
	text text,
	date date,
	compliment_count smallint,
	user_id varchar(30),
	business_id varchar(30),
	--FOREIGN KEY (user_id) REFERENCES user_yelp,
	--FOREIGN KEY (business_id) REFERENCES business	
);

select * from tip;

drop table target_city;
create table target_city(	
	state varchar (5),
	city varchar(60),
	PRIMARY KEY (state, city)
);


insert into target_city values ('SC','Charleston');
insert into target_city values ('FL','Miami');
insert into target_city values ('FL','Tampa');
insert into target_city values ('MA','Boston');
insert into target_city values ('WA','Seattle');
insert into target_city values ('CA','San Diego');
insert into target_city values ('PE','New Orleans');

		 
		 
		 
select * from target_city; 
		 
		 

drop table state_city;
create table state_city(
	state varchar (5),
	city varchar(60),
	nicknames text,
	PRIMARY KEY (state, city)
);

insert into state_city values('FL', 'Tampa', 'Tampa,Tampa Bay');
insert into state_city values('SC', 'Tampa', 'Tampa,Tampa Bay');
insert into state_city values('MA', 'Tampa', 'Tampa,Tampa Bay');
insert into state_city values('TX', 'Tampa', 'Tampa,Tampa Bay');
insert into state_city values('TX', 'Tampa', 'Tampa,Tampa Bay');


select distinct city from business
where state = 'WA';

