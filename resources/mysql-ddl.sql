create schema icd_service collate utf8mb4_0900_ai_ci;

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
            on delete set null
);

create table ICD_11
(
    ID_DISEASE mediumint                null,
    CODE       varchar(20) charset utf8 not null,
    constraint ICD_11_ID_DISEASE_uindex
        unique (ID_DISEASE),
    constraint ICD_11_DISEASES_ID_DISEASE_fk
        foreign key (ID_DISEASE) references DISEASES (ID_DISEASE)
            on delete set null
);

create table WIKI
(
    ID_DISEASE mediumint                 null,
    ENG_TITLE  varchar(512) charset utf8 null,
    PL_TITLE   varchar(512) charset utf8 null,
    ENG_LINK   varchar(128) charset utf8 null,
    PL_LINK    varchar(128) charset utf8 null,
    constraint WIKI_ID_DISEASE_uindex
        unique (ID_DISEASE),
    constraint ID_DISEASE
        foreign key (ID_DISEASE) references DISEASES (ID_DISEASE)
);
