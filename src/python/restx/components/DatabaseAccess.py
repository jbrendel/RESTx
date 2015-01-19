"""
RESTx: Sane, simple and effective data publishing and integration. 

Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version. 

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details. 

You should have received a copy of the GNU General Public License 
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

"""

"""
A database access component, using JDBC

"""
# Imports all aspects of the API
from restx.components.api import *
from java.sql             import *
from java.lang            import Class

class DatabaseAccess(BaseComponent):
    NAME             = "DatabaseAccess"
    DOCUMENTATION    = """
Accesses to an SQL database.


This component provides access to a database via JDBC. Therefore, the proper
JDBC driver should be in the classpath (for example by placing it into the
RESTx lib/ directory. The class name of the driver needs to be specified during
resource creation time.


CURRENT LIMITATIONS:


 * This component only allows for queries on a single table.

 * The table has to have an auto-incrementing, numeric unique ID column. The
 name of this column needs to be specified during resource creation time.

 * Currently does not use bound variables and only does a very superficial
 way of checking for injection. This will be updated soon! In the meantime,
 since parameters are provided in-house during resource creation (done by a
 trusted resource) and not via the request URI when accessing elements, this
 is slightly less critical. However, we will get around to change that.


USAGE NOTES:


Instead of specifying a single query string, the columns, table and where
clause(s) are specified as separate parameters. This makes it easier to create
specialized components (partial resources), where some of these things are pre-
defined already. For example, IT may create a specialized component with a
pre-determined value for the table and one where clause. Other users can then
create their own resources, but are limited to that table and to the selection
that results from that first where clause.


For example:


Imagine a 'customer' table. IT may create a specialized component, which fixes
the 'table' parameter and one of the 'where' clauses, so that only customers
within a particular state are returned. By leaving the tables unset (leaving
them at '*'), the resulting query may look like this:


    SELECT * FROM customer WHERE state='CA';


Based on this specialized component, others may then create additional
resources. The table name and that one where clause for the state cannot be
changed anymore, but they are free to specify particular columns and a further
where clause. For example, for columns they may specify 'name' and 'phone' and
for an additional where clause they may enter 'total_order_value > 1000000'.


The complete query then looks like this:


    SELECT name, phone FROM customer WHERE state='CA' and total_order_value > 1000000;


Additional parameters:


id_column :        The name of the column which holds the unique ID (key) of the table
                   entries. This is used as handle when referring to individual rows
                   for GET or PUT methods.


allow_updates :    If set to 'yes' then we are allowing the creation of new entries via
                   POST and update of existing entries via PUT.


name_value_pairs : If set then we return each table row as a dictionary with the column
                   name as key. This is easy to read and process, but can increase the
                   volume of the returned data. If it's set to 'No' then we return the
                   individual elements of each row just as a plain list.

"""



    DESCRIPTION    = "Service methods and capabilities to access a SQL database"

    PARAM_DEFINITION = {
                           "jdbc_driver_class"    : ParameterDef(PARAM_STRING,  "The classname of the driver (for example: com.mysql.jdbc.Driver)", required=True),
                           "db_connection_string" : ParameterDef(PARAM_STRING,  "The database connection string", required=True),
                           "table_name"           : ParameterDef(PARAM_STRING,  "Name of the DB table.", required=True),
                           "columns"              : ParameterDef(PARAM_STRING,  "Comma separated list of DB columns for the result, or '*' for all", required=False, default="*"),
                           "id_column"            : ParameterDef(PARAM_STRING,  "Name of the column that holds the unique ID", required=True),
                           "where1"               : ParameterDef(PARAM_STRING,  "Optional WHERE clause (SQL syntax)", required=False, default=""),
                           "where2"               : ParameterDef(PARAM_STRING,  "Additional optional WHERE clause (SQL syntax)", required=False, default=""),
                           "allow_updates"        : ParameterDef(PARAM_BOOL,    "Can the user create new entries or update existing ones?", required=False, default=False),
                           "name_value_pairs"     : ParameterDef(PARAM_BOOL,    "Return name/value pairs if set, otherwise plain lists", required=False, default=True),
                       }
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           "entries" : {
                               "desc" : "The stored entries. You can POST a new entry, PUT an update, GET or DELETE an existing one. For PUT, GET and DELETE the ID of the entry needs to be specified as the 'id' parameter.",
                               "params" : {
                                   "id"  : ParameterDef(PARAM_NUMBER, "The ID of the entry, needed for PUT and (optionally) GET", required=False, default=-1),
                               },
                               "positional_params": [ "id" ],
                               "output_types" : [ "application/json", "application/xml", "text/html", "text/csv", "application/ext+json" ],
                               "input_types" : [ "application/json", "application/x-www-form-urlencoded", "application/ext+json" ],
                               #"input_types" : None,
                           }
                       }

    CONNECTION_CACHE = dict()

    def __get_connection(self):
        if self.db_connection_string in DatabaseAccess.CONNECTION_CACHE:
            connection, table_columns = DatabaseAccess.CONNECTION_CACHE[self.db_connection_string]
        else:
            # Establish the connection
            Class.forName(self.jdbc_driver_class)
            connection = DriverManager.getConnection(self.db_connection_string)

            # Get the column names
            meta = connection.getMetaData()
            res  = meta.getColumns(None, None, self.table_name, None);
            table_columns = []
            while (res.next()):
                table_columns.append(res.getString("COLUMN_NAME"))

            res.close()

            # Store the connection and column info in the cache
            DatabaseAccess.CONNECTION_CACHE[self.db_connection_string] = (connection, table_columns)

        return connection, table_columns

    def __column_sanity_check(self, columns):
        elems = columns.split(",")
        cols = []
        for e in elems:
            e = e.strip()
            if " " in e  or  "(" in e  or  ")" in e  or  ";" in e:
                raise RestxException("Malformed columns")
            cols.append(e)
        return cols

    def __get_where_str(self, id=None):
        if self.where2 != "-" and (self.where1 == "-"  or  not self.where1):
            # Making sure that where1 is set
            self.where1 = self.where2
            self.where2 = None
        if self.where1  and  self.where1 != "-":
            if id and id > -1:
                where_str = " WHERE %s AND %s=%s" % (self.where1, self.id_column, id)
            else:
                where_str = " WHERE %s" % self.where1
            if self.where2  and  self.where2 != "-":
                where_str += " AND %s" % self.where2
        else:
            if id and id > -1:
                where_str = " WHERE %s=%s" % (self.id_column, id)
            else:
                where_str = ""
        return where_str


    def __get_entry(self, connection, table_columns, resource_columns, id):
        #
        # Getting data
        #
        # 'resource_columns' is a list of the column names, which are defined as comma-separated
        # string in self.columns
        #
        where_str   = self.__get_where_str(id)
        stmt        = connection.createStatement()
        cmd_str     = str("SELECT %s FROM %s%s" % (self.columns, self.table_name, where_str))
        results     = stmt.executeQuery(cmd_str)
        data        = []
        while (results.next()):
            col_results = [ results.getObject(resource_columns.index(col_name)+1) for col_name in resource_columns ]
            if self.name_value_pairs:
                row_data = dict(zip(resource_columns, col_results))
            else:
                row_data = col_results
            data.append(row_data)

        if id and id > -1:
            # Only one result
            if len(data) == 0:
                return Result.notFound("Could not find entity with id '%s'" % id)
            elif len(data) > 1:
                return Result.internalServerError("Data inconsistency")
            else:
                data = data[0]

        return Result.ok(data)

    def __post_entry(self, connection, obj, colnames):
        colstr    = ', '.join(colnames)
        valstr    = ', '.join([(str(obj[k]) if type(obj[k]) in [int, long, float] else "'%s'" % obj[k]) for k in colnames ])
        stmt      = connection.createStatement()
        cmd_str   = str("INSERT INTO %s (%s) VALUES (%s)" % (self.table_name, colstr, valstr))
        res       = stmt.executeUpdate(cmd_str, Statement.RETURN_GENERATED_KEYS)
        if res == 0:
            return Result.internalServerError("Cannot create new entry.")
        generated_keys = stmt.getGeneratedKeys()
        generated_keys.next()
        new_id = generated_keys.getLong(1)
        stmt.close()
        return Result.created(str(Url("%s/%d" % (self.getMyResourceUri(), new_id))))

    def __put_entry(self, connection, obj, colnames, id):
        # Check that this element exists in the database
        # The new ID we will use to store this object
        stmt    = connection.createStatement()
        cmd_str = str("SELECT count(*) FROM %s WHERE %s=%d" % (self.table_name, self.id_column, id))
        res     = stmt.executeQuery(cmd_str)
        res.next()
        num     = res.getInt(1)
        stmt.close()
        if num > 1:
            return Result.internalServerError("Data inconsistency")
        elif num == 0:
            return Result.notFound("Entry with id '%d' cannot be found" % id)

        colsets = ', '.join([ ("%s=%s" % (k, (str(obj[k]) if type(obj[k]) in [int, long, float] else "'%s'" % obj[k]))) for k in colnames ])
        cmd_str = str("UPDATE %s SET %s WHERE %s=%d" % (self.table_name, colsets, self.id_column, id))
        stmt    = connection.createStatement()
        res = stmt.executeUpdate(cmd_str)
        stmt.close()
        if res > 0:
            return Result.ok("Updated %d columns" % res)
        else:
            return Result.notFound("Could not find entry '%d' for update." % id)

    def __delete_entry(self, connection, id):
        # Check that this element exists in the database
        # The new ID we will use to store this object
        stmt    = connection.createStatement()
        cmd_str = str("DELETE FROM %s WHERE %s=%d" % (self.table_name, self.id_column, id))
        res     = stmt.executeUpdate(cmd_str)
        stmt.close()
        if res > 0:
            return Result.ok("Deleted %d columns" % res)
        else:
            return Result.notFound("Could not find entry '%d' for deletion." % id)
     
    def entries(self, method, input, id):
        """
        Represents the 'entries' resource of this database table.

        This is used to GET one or more entries, to POST (create) a
        new entry or to update an existing entry.

        """

        connection, table_columns = self.__get_connection()

        if self.columns  and  self.columns != "*":
            resource_columns = self.__column_sanity_check(self.columns)
        else:
            resource_columns = table_columns

        if method == HttpMethod.GET  or  (method == HttpMethod.POST  and  "xaction=read" in input):
            #
            # Getting data
            #
            return self.__get_entry(connection, table_columns, resource_columns, id)

        elif self.allow_updates:

            if method in [ HttpMethod.POST, HttpMethod.PUT ]:
                #
                # Creating a new entry or updating an existing one
                #
                obj = input
                if type(obj) is not dict:
                    return Result.badRequest("Format error: Excpected JSON dictionary as input")

                if method == HttpMethod.POST:
                    # Creating a new one?
                    if id > 0:
                        return Result.badRequest("Cannot specify ID when creating a new entry (ID is determined by server)")

                # We set the ID ourselves, just quietly remove it if it was specified through the request
                if self.id_column in obj:
                    del obj[self.id_column]

                # Check whether we actually passed some information in, or if it's all empty
                if not obj:
                    return Result.badRequest("Format error: No information in request")

                # Getting the column names for the table and making sure that we are
                # only referring to existing columns
                for name in obj.keys():
                    if name not in table_columns:
                        return Result.badRequest("Unknown column '%s' in input" % name)

                # Some sanity checking on those
                for name, value in obj.items():
                    for illegal in ";*()":
                        if illegal in name:
                            return Result.badRequest("Illegal character in column name: " + name)
                        if type(value) in [ str, unicode ]:
                            if illegal in value:
                                return Result.badRequest("Illegal character in value for column '%s'" % name)

                # Get the properly ordered list of columns that we have actually specified.
                # This allows us to ommit optional values.
                cols = [ name for name in table_columns if name in obj ]

                if method == HttpMethod.POST:
                    return self.__post_entry(connection, obj, cols)
                else:
                    return self.__put_entry(connection, obj, cols, id)

            elif method == HttpMethod.DELETE:
                #
                # Deleting an existing entry
                #
                if id < 1:
                    return Result.badRequest("Need to specify a valid entry ID for delete.")
                return self.__delete_entry(connection, id)

        else:
            return Result.unauthorized("You don't have permission to modify this resource")


