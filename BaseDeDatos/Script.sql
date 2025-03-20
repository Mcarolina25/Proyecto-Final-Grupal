drop table sitios;

create table sitios(
	gmap_id varchar(80) primary key,
	category text,
	name text,
	address varchar(101),
	descripcion varchar(100) ,
	latitude varchar(20),
	longitude varchar(20),
	avg_rating float,
	num_of_reviews numeric,
	price float,
	hours text,
	"MISC" text,
	state varchar(25),
	relative_results text,
	URL text,
	description text
);

select * from sitios;

create table business(
	business_id varchar(20) primary key,
	name varchar(20),
	address varchar(20),
	city varchar(20),
	state varchar(25),
	postal_code varchar(10),
	latitude varchar(20),
	longitude varchar(20),
	starts float,
	review_count smallint,
	is_open smallint,
	object json,
	categories json,
	hour json
);

select * from business;

create table user_yelp(
	user_id varchar(30) primary key,
	name varchar(20),
	review_count smallint,
	yelping_since date,
	friends json,
	useful smallint,
	funny smallint,
	cool smallint,
	fans smallint,
	elite json,
	average_starts float,
	compliment_hot smallint,
	compliment_more smallint,
	compliment_profile smallint,
	compliment_cute smallint,
	compliment_list smallint,
	compliment_note smallint,
	compliment_plain smallint,
	compliment_cool smallint,
	compliment_funny smallint,
	compliment_writer smallint,
	compliment_photos smallint
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



create table review(
	review_id numeric primary key,
	starts smallint,
	date_review date,
	text_review text,
	useful smallint,
	funny smallint,
	cool smallint,
	user_id varchar(30),
	business_id varchar(20),
	FOREIGN KEY (user_id) REFERENCES user_yelp,
	FOREIGN KEY (business_id) REFERENCES business	
);

select * from review;

drop table checkin;
create table checkin(
	checkin_id serial primary key,
	date_checkin date[],
	business_id varchar(20),
	FOREIGN KEY (business_id) REFERENCES business	
);

select * from checkin;

drop table tip;
create table tip(
	tip_id serial primary key,
	text_tip text,
	date_tio date,
	compliment_count smallint,
	user_id varchar(30),
	business_id varchar(20),
	FOREIGN KEY (user_id) REFERENCES user_yelp,
	FOREIGN KEY (business_id) REFERENCES business	
);

select * from tip;

