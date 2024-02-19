from flask import jsonify
import re




class MySQLExceptionHandler:
    def __init__(self) -> None:
        pass
    
    @classmethod
    def uk_write_error(self, e: Exception) -> jsonify:
        '''
        e.args[0] :
            (pymysql.err.IntegrityError) (1062, "Duplicate entry '123456' for key 'token.token'")
        '''
        query_string1 = '1062, "Duplicate entry\D*'
        query_string2 = "for key \\'\D*'"
        rex1 = re.search(query_string1, e.args[0])
        rex2 = re.search(query_string2, e.args[0])
        if rex1:
            if rex2:
                uk_error_column = rex2.group().split("'")[1]
                return jsonify(status=False, message="Uk Error {}".format(uk_error_column), code=403.1), 403
            return jsonify(status=False, message="Uk Error", code=403.1), 403
        
    @classmethod
    def fk_write_error(self, e: Exception) -> jsonify:
        '''
        e.args[0] :
            (pymysql.err.IntegrityError) 
            (1452, 'Cannot add or update a child row: a foreign key constraint fails 
            (`token_db`.`token_permission`, CONSTRAINT `token_permission_ibfk_1` FOREIGN KEY 
            (`permission_id`) REFERENCES `permission` (`id`))')
        '''
        query_string1 = "Cannot add or update a child row: a foreign key constraint fails"
        query_string2 = "FOREIGN KEY\s\W*\D*REFERENCES"
        rex1 = re.search(query_string1, e.args[0])
        rex2 = re.search(query_string2, e.args[0])
        if rex1:
            if rex2:
                fk_error_column = rex2.group().split("(`")[1].split("`)")[0]
                return jsonify(status=False, message="Fk Error {}".format(fk_error_column), code=403.1), 403
        return jsonify(status=False, message="Uk Error", code=403.1), 403
        