create table DISEASES
(
    ID_DISEASE mediumint primary key auto_increment,
    NAME       varchar(256) charset utf8 null,
    constraint DISEASES_ID_DISEASE_uindex
        unique (ID_DISEASE),
    constraint DISEASES_NAME_uindex
        unique (NAME)
);

create table ADDITIONAL_INFO
(
    ID_DISEASE         mediumint    null,
    ID_ADDITIONAL_INFO mediumint primary key auto_increment,
    TYPE               varchar(32)  not null,
    AUTHOR             varchar(128) not null,
    INFO               text         not null,
    constraint ADDITIONAL_INFO_ID_ADDITIONAL_INFO_uindex
        unique (ID_ADDITIONAL_INFO),
    constraint ADDITIONAL_INFO_DISEASES_ID_DISEASE_fk
        foreign key (ID_DISEASE) references DISEASES (ID_DISEASE)
            on delete cascade
);

create table ICD_10
(
    ID_DISEASE mediumint                null,
    CODE       varchar(20) charset utf8 not null,
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

create table DISEASES_REL
(
    ID_REL       int primary key auto_increment,
    ID_DISEASE_1 mediumint   not null,
    ID_DISEASE_2 mediumint   not null,
    REL_TYPE     varchar(64) not null,
    constraint DISEASES_REL_ID_REL_uindex
        unique (ID_REL),
    constraint DISEASES_REL_DISEASES_ID_DISEASE_1_ID_DISEASE_fk
        foreign key (ID_DISEASE_1) references DISEASES (ID_DISEASE)
            on delete cascade,
    constraint DISEASES_REL_DISEASES_ID_DISEASE_2_ID_DISEASE_fk
        foreign key (ID_DISEASE_2) references DISEASES (ID_DISEASE)
            on delete cascade
);
