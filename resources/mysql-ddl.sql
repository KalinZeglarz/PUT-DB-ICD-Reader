create table DISEASES
(
    ID_DISEASE mediumint auto_increment,
    NAME       varchar(256) charset utf8 null,
    constraint DISEASES_ID_DISEASE_uindex
        unique (ID_DISEASE),
    constraint DISEASES_NAME_uindex
        unique (NAME)
);

alter table DISEASES
    add primary key (ID_DISEASE);

create table ADDITIONAL_INFO
(
    ID_DISEASE         mediumint    null,
    ID_ADDITIONAL_INFO mediumint auto_increment,
    TYPE               varchar(32)  not null,
    AUTHOR             varchar(128) not null,
    INFO               text         not null,
    constraint ADDITIONAL_INFO_ID_ADDITIONAL_INFO_uindex
        unique (ID_ADDITIONAL_INFO),
    constraint ADDITIONAL_INFO_DISEASES_ID_DISEASE_fk
        foreign key (ID_DISEASE) references DISEASES (ID_DISEASE)
            on delete cascade
);

alter table ADDITIONAL_INFO
    add primary key (ID_ADDITIONAL_INFO);

create table ICD_10
(
    ID_DISEASE mediumint               null,
    CATEGORY   varchar(4) charset utf8 not null,
    DETAILS    varchar(4) charset utf8 null,
    EXTENSION  varchar(2) charset utf8 null,
    constraint ICD_10_ID_DISEASE_uindex
        unique (ID_DISEASE),
    constraint ICD_10_DISEASES_ID_DISEASE_fk
        foreign key (ID_DISEASE) references DISEASES (ID_DISEASE)
            on delete cascade
);

create table ICD_11
(
    ID_DISEASE mediumint                null,
    CODE       varchar(20) charset utf8 not null,
    constraint ICD_11_ID_DISEASE_uindex
        unique (ID_DISEASE),
    constraint ICD_11_DISEASES_ID_DISEASE_fk
        foreign key (ID_DISEASE) references DISEASES (ID_DISEASE)
            on delete cascade
);

create table WIKI
(
    ID_DISEASE mediumint    null,
    LANGUAGE   varchar(4)   null,
    TITLE      varchar(256) null,
    LINK       varchar(512) null,
    constraint WIKI_TEMP_DISEASES_ID_DISEASE_fk
        foreign key (ID_DISEASE) references DISEASES (ID_DISEASE)
            on delete cascade
);
