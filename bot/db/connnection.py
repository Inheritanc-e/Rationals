import logging 
import typing as t 

import asyncpg 


logger = logging.getLogger(__name__)

class Connection:
    """A context manager class which creates and releases connection pools."""
    def __init__(self, pool:asyncpg.Pool):
        self.pool = pool
        self.is_in_use = False
        
    async def __aenter__(self):
        self.is_in_use = True
        self.conn = await self.pool.acquire()
        return self.conn
    
    async def __aexit__(self, exc_t, exc_v, exc_tb):
        if self.is_in_use:
            await self.pool.release(self.conn)
            self.is_in_use = False

class Tables:
    """A class responsible for making insertion of data easier."""
    
    def __init__(self,table_name, pool): 
        self.table_name = table_name
        self.pool = pool
        
    async def get_column_info(self) -> dict:
        """Returns a dictionary containing column information."""
        async with self.pool.acquire() as ac:
            column_types = await ac.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1", self.table_name)
            column_nullable = await ac.fetch("SELECT column_name, columns.is_nullable FROM information_schema.columns WHERE table_name = $1", self.table_name)

            column_type = {x[0]: x[1] for x in [list(y.values()) for y in column_types]}

            columns_is_nullable = {x[0]: x[1] == 'YES' for x in [list(y.values()) for y in column_nullable]}


            return {x: {'data_type':column_type[x], 
                        'is_nullable': columns_is_nullable[x]} for x in column_type}

    async def insert(self, **kwargs:dict):
        """Inserts the provided data into the given table."""
        verified = {} #verified columns
        column_info_ = await self.get_column_info()

        #check column names
        for column in column_info_.keys():
            try:
                value = kwargs[column]
            except KeyError:
                logger.info(f"{column.title()} not present in provided values. ")
                continue

            check = column_info_[column]['data_type']
            if value is None and not check:
                raise TypeError(f"Cannot pass None to non nullable for column {column}")

            verified[column] = value
            insert_statement = f"INSERT INTO {self.table_name} ({', '.join(verified)}) VALUES ({', '.join((f'${x}' for x in range(1, len(verified)+1)))})"

        try:
            async with Connection(self.pool) as connection:
                await connection.execute(insert_statement, *verified.values())
            logger.info(f'INSERT 0 1 for table {self.table_name}')

        except Exception as e:
            logger.error(
                f"Failed to insert into table {self.table_name}", 
                exc_info = (type(e), e, e.__traceback__)
            )
    
    async def update(self, condition:list, **kwargs:dict):
        """Updates the data present in the table."""
        column_info_ = await self.get_column_info()
        
        for column in column_info_.keys():
            if column not in column_info_.keys():
                raise KeyError 

        condition_dict = dict(condition)
        where_statement = "WHERE "

        for index_ , key in enumerate(condition_dict, start=1):
            where_statement += f"{key} = ${index_}" if '=' not in where_statement else f" AND {key} = ${index_}"

        #checking if the where statement works
        async with Connection(self.pool) as connection:
            connection.fetch(f"SELECT * FROM {self.table_name} {where_statement}", *condition_dict.values())

        logger.info("WHERE condition passed for update values.")

        set_statement = "SET "
        for index_ , key in enumerate(kwargs, start=1):
            set_statement += f"{key} = ${index_}" if '=' not in where_statement else f", {key} = ${index_}"

        update_statement = f'UPDATE {self.table_name} {set_statement}'

        try:
            async with Connection(self.pool) as connection:
                connection.execute(update_statement, *kwargs.values())
            logger.info('UPDATE 0 1')
        except Exception as e:
            logger.error(f"Failed to update columns: {', '.join(kwargs.keys())} for table {self.table_name}", 
                exc_info = (type(e), e, e.__traceback__))
    
    @property
    def to_dict(self, record_object: asyncpg.Record) -> list:
        """
        Converts the retrieved record into a dictionary. 
        """
        return [dict(x.items()) for x in record_object]    

    @property
    def from_dict(self, data, dict_object:list) -> dict:
        """Returns a dict containing the required data if it exists."""
        for item in dict_object:
            return item if data in item.keys() or data in item.values() else False