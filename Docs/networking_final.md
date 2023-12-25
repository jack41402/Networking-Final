classDiagram
direction BT
class comment {
   varchar(1000) content
   datetime time
   int author_id
   int reply_id
   int comment_id
}
class directory {
   int user_id
   varchar(45) ip
   int port
   int id
}
class file {
   varchar(100) name
   varchar(20) type
   blob data
   datetime time
   int author_id
   int reply_id
   int file_id
}
class friend {
   int user_id
   int friend_id
   varchar(5) status
   int id
}
class user_information {
   varchar(50) username
   varchar(50) password
   int user_id
}

comment  -->  user_information : author_id:user_id
comment  -->  user_information : reply_id:user_id
directory  -->  user_information : user_id
file  -->  user_information : author_id:user_id
file  -->  user_information : reply_id:user_id
friend  -->  user_information : user_id
friend  -->  user_information : friend_id:user_id
