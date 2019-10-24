create table facebook_post(
	id varchar(30),
    scrap_time datetime,
    contents varchar(1000),
    post_time varchar(30),
    username varchar(30),
    likes int,
    best3_react varchar(50),
    comments int,
    shares int
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
alter table facebook_post add primary key(id, scrap_time);

create table facebook_Influencer(
	username varchar(50),
    scrap_time datetime,
    followers int,
    likers int
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
alter table facebook_Influencer add primary key(username, scrap_time);

select * from facebook_Influencer;
select * from facebook_post;