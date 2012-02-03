'''    
Created on 12 April 2011
@author: jog
'''

import MySQLdb
import ConfigParser
import hashlib
import logging
import time
log = logging.getLogger( "console_log" )


#///////////////////////////////////////


def safety_mysql( fn ) :
    """ I have included this decorator because there are no 
    gaurantees the user has mySQL setup so that it won't time out. 
    If it does time out, this function remedies it, by trying a
    (one shot) attempt to reconnect the database.
    """

    def wrapper( self, *args, **kwargs ) :
        try:
            return fn( self, *args, **kwargs )
        except MySQLdb.Error, e:
            if e[ 0 ] == 2006:
                self.reconnect()
                return fn( self, *args, **kwargs )
            else:
                raise e 

    return wrapper
    

#///////////////////////////////////////

    
class CatalogDB( object ):
    ''' classdocs '''
    
    DB_NAME = 'catalog'
    
    TBL_CATALOG_USERS = 'tblCatalogUsers'
    TBL_CATALOG_CLIENTS = 'tblCatalogClients'
    TBL_CATALOG_RESOURCES = 'tblCatalogResources'
    TBL_CATALOG_INSTALLS = 'tblCatalogInstalls'    
    TBL_CATALOG_REQUESTS = 'tblCatalogRequests'
    
    CONFIG_FILE = "catalog.cfg"
    SECTION_NAME = "CatalogDB"
    
    
    #///////////////////////////////////////

            
    createQueries = { 
               
        TBL_CATALOG_USERS : """
            CREATE TABLE %s.%s (
                user_id varchar(256) NOT NULL,
                user_name varchar(64),
                email varchar(256),
                registered int(10) unsigned,            
                PRIMARY KEY (user_id), UNIQUE KEY `UNIQUE` (`user_name`) 
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_CATALOG_USERS ),
        
        
        TBL_CATALOG_RESOURCES : """
            CREATE TABLE %s.%s (
                resource_id varchar(256) NOT NULL,
                resource_name varchar(128) NOT NULL,
                redirect_uri varchar(256) DEFAULT NULL,
                description varchar(1024) DEFAULT NULL,
                logo_uri varchar(256) DEFAULT NULL,
                web_uri varchar(256) DEFAULT NULL,
                namespace varchar(45) DEFAULT NULL,
                registered int(10) unsigned NOT NULL, 
                PRIMARY KEY (resource_id),
                UNIQUE KEY `UNIQUE` (resource_name) 
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_CATALOG_RESOURCES), 


        TBL_CATALOG_INSTALLS: """
            CREATE TABLE %s.%s (
                user_id varchar(256) NOT NULL,
                resource_id varchar(256) NOT NULL,
                state varchar(256),
                access_token varchar(256),
                auth_code varchar(256),
                created int(10) unsigned,
                ctime int(10) unsigned,     
                PRIMARY KEY (user_id, resource_id), 
                FOREIGN KEY (resource_id) REFERENCES %s(resource_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;            
        """  % ( DB_NAME, TBL_CATALOG_INSTALLS, TBL_CATALOG_RESOURCES ),
        
        
        TBL_CATALOG_CLIENTS : """
            CREATE TABLE %s.%s (
                client_id varchar(256) NOT NULL,
                client_name varchar(128) NOT NULL,
                redirect_uri varchar(256) DEFAULT NULL,
                description varchar(1024) DEFAULT NULL,
                logo_uri varchar(256) DEFAULT NULL,
                web_uri varchar(256) DEFAULT NULL,
                namespace varchar(45) DEFAULT NULL,
                registered int(10) unsigned NOT NULL, 
                PRIMARY KEY (client_id),
                UNIQUE KEY `UNIQUE` (client_name) 
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_CATALOG_CLIENTS),  
        
        
        TBL_CATALOG_REQUESTS : """
            CREATE TABLE %s.%s (
                request_id int(10) unsigned NOT NULL AUTO_INCREMENT,
                user_id varchar(256) NOT NULL,
                client_id varchar(256) NOT NULL,
                state varchar(256),
                resource_id varchar(256) NOT NULL,
                redirect_uri varchar(256) NOT NULL,            
                expiry_time int(10) unsigned NOT NULL,
                query text NOT NULL,
                checksum varchar(256) NOT NULL,
                request_status varchar(32) NOT NULL,
                access_token varchar(256),
                auth_code varchar(256),
                created int(10) unsigned,
                ctime int(10) unsigned,     
                PRIMARY KEY (request_id),
                UNIQUE KEY `UNIQUE` (user_id, client_id, checksum), 
                FOREIGN KEY (user_id, resource_id) REFERENCES %s(user_id, resource_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_CATALOG_REQUESTS, TBL_CATALOG_INSTALLS ),      
    } 
    
        
    #///////////////////////////////////////
    
    
    def __init__( self, name = "CatalogDB" ):
            
        #MysqlDb is not thread safe, so program may run more
        #than one connection. As such naming them is useful.
        self.name = name
        
        Config = ConfigParser.ConfigParser()
        Config.read( self.CONFIG_FILE )
        self.hostname = Config.get( self.SECTION_NAME, "hostname" )
        self.username =  Config.get( self.SECTION_NAME, "username" )
        self.password =  Config.get( self.SECTION_NAME, "password" )
        self.dbname = Config.get( self.SECTION_NAME, "dbname" )
        self.connected = False;

        
    #///////////////////////////////////////
    

    def connect( self ):
        
        log.info( "%s: connecting to mysql database..." % self.name )

        self.conn = MySQLdb.connect( 
            host=self.hostname,
            user=self.username,
            passwd=self.password,
            db=self.dbname
        )
 
        self.cursor = self.conn.cursor( MySQLdb.cursors.DictCursor )
        self.connected = True
                    
                    
    #///////////////////////////////////////
    
    
    def reconnect( self ):
        log.info( "%s: Database reconnection process activated..." % self.name );
        self.close()
        self.connect()
        

    #///////////////////////////////////////
          
          
    @safety_mysql                
    def commit( self ) : 
        self.conn.commit();
        
        
    #///////////////////////////////////////
        

    def close( self ) :   
        if self.conn.open:
            log.info( "%s: disconnecting from mysql database..." % self.name );
            self.cursor.close();
            self.conn.close()
                     
   
    #///////////////////////////////////////
    
    
    @safety_mysql        
    def check_tables( self ):
        
        log.info( "%s: checking system table integrity..." % self.name );
        
        #-- first check that the database itself exists        
        self.cursor.execute ( """
            SELECT 1
            FROM information_schema.`SCHEMATA`
            WHERE schema_name='%s' """ % self.DB_NAME )
                
        row = self.cursor.fetchone()
        if ( row is None ):
            log.info( "%s: database does not exist - creating..." % self.name );    
            self.cursor.execute ( "CREATE DATABASE catalog" )
        
        #then check it is populated with the required tables
        self.cursor.execute ( """
            SELECT table_name
            FROM information_schema.`TABLES`
            WHERE table_schema='%s' """ % self.DB_NAME )
        
        tables = [ row[ "table_name" ] for row in self.cursor.fetchall() ]
        
        #if they don't exist for some reason, create them.    
        for t, q in self.createQueries.iteritems():
            if not t in tables : 
                log.warning( "%s: Creating missing system table: '%s'" % ( self.name, t ) );
                self.cursor.execute( q )
        
        self.commit()
        
        
    #////////////////////////////////////////////////////////////////////////////////////////////


    @safety_mysql   
    def insert_client_registration( self, client_id, client_name,
        redirect_uri, description, logo_uri, web_uri, namespace):
       
        query = """
             INSERT INTO %s.%s VALUES ( %s, %s, %s, %s, %s, %s, %s, %s )
        """  % ( self.DB_NAME, self.TBL_CATALOG_CLIENTS, 
                 '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ) 

        #client_id, user_id and checksum must be unique, to prevent duplicate queries
        self.cursor.execute( 
            query, ( 
                client_id,
                client_name,
                redirect_uri, 
                description, 
                logo_uri, 
                web_uri,
                namespace,
                time.time()
            ) 
        )
        
        
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_client_by_id( self, client_id ) :
        if not client_id: return None
        query = "SELECT * FROM %s.%s WHERE client_id = %s" % \
            ( self.DB_NAME, self.TBL_CATALOG_CLIENTS, '%s', )
        self.cursor.execute( query, ( client_id, ) )
        return self.cursor.fetchone()
        
    
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_client_by_name( self, client_name ) :
        if not client_name: return None
        query = "SELECT * FROM %s.%s WHERE client_name = %s" % \
            ( self.DB_NAME, self.TBL_CATALOG_CLIENTS, '%s', )
        self.cursor.execute( query, ( client_name, ) )
        return self.cursor.fetchone()   
                      
  
    #////////////////////////////////////////////////////////////////////////////////////////////


    @safety_mysql   
    def insert_resource_registration( self, resource_id, resource_name,
        redirect_uri, description, logo_uri, web_uri, namespace):
       
        query = """
             INSERT INTO %s.%s VALUES ( %s, %s, %s, %s, %s, %s, %s, %s )
        """  % ( self.DB_NAME, self.TBL_CATALOG_RESOURCES, 
                 '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', ) 
         
        #client_id, user_id and checksum must be unique, to prevent duplicate queries
        self.cursor.execute( 
            query, ( 
                resource_id,
                resource_name,
                redirect_uri, 
                description, 
                logo_uri, 
                web_uri,
                namespace,
                time.time()
            ) 
        )
        
        
    #////////////////////////////////////////////////////////////////////////////////////////////
    
    @safety_mysql   
    def insert_install( self, user_id, resource_id,
        state, access_token, auth_code ):

        query = """
             INSERT INTO %s.%s VALUES ( %s, %s, %s, %s, %s, %s, %s )
        """  % ( self.DB_NAME, self.TBL_CATALOG_INSTALLS, 
                 '%s', '%s', '%s', '%s', '%s', '%s', '%s', ) 
        
        #client_id, user_id and checksum must be unique, to prevent duplicate queries
        self.cursor.execute( 
            query, ( 
                user_id,
                resource_id,
                state, 
                access_token, 
                auth_code, 
                time.time(),
                time.time(),                
            ) 
        )
        
        
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_install( self, user_id, resource_id ) :
        
        if not resource_id: return None
        query = "SELECT * FROM %s.%s WHERE user_id = %s AND resource_id = %s" % \
            ( self.DB_NAME, self.TBL_CATALOG_INSTALLS, '%s', '%s' )
        self.cursor.execute( query, ( user_id, resource_id, ) )
        return self.cursor.fetchone()
    
    
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_install_by_name( self, user_id, resource_name ) :

        if not resource_name: return None
        query = """
                SELECT * FROM %s.%s i, %s.%s r 
                WHERE i.user_id = %s 
                AND i.resource_id = r.resource_id
                AND r.resource_name = %s
            """ % \
            ( self.DB_NAME, self.TBL_CATALOG_INSTALLS,
              self.DB_NAME, self.TBL_CATALOG_RESOURCES, 
               '%s', '%s' )

        self.cursor.execute( query, ( user_id, resource_name, ) )

        return self.cursor.fetchone()
    
    
        
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_resource_by_id( self, resource_id ) :
        
        if not resource_id: return None
        query = "SELECT * FROM %s.%s WHERE resource_id = %s" % \
            ( self.DB_NAME, self.TBL_CATALOG_RESOURCES, '%s', )
        self.cursor.execute( query, ( resource_id, ) )
        return self.cursor.fetchone()
        
    
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_resource_by_name( self, resource_name ) :
        
        if not resource_name: return None
        query = "SELECT * FROM %s.%s WHERE resource_name = %s" % \
            ( self.DB_NAME, self.TBL_CATALOG_RESOURCES, '%s', )
        self.cursor.execute( query, ( resource_name, ) )
        return self.cursor.fetchone()   
    
    
    #////////////////////////////////////////////////////////////////////////////////////////////


    @safety_mysql   
    def insert_access_request( self, 
        user_id, client_id, state, redirect_uri,
        resource_name, expiry_time, query_code, request_status ):
       
        #create a SHA checksum for the file
        checksum = hashlib.sha1( query_code ).hexdigest()

        query = """
             INSERT INTO %s.%s VALUES 
             ( null, %s, %s, %s, %s, %s, %s, %s, %s, %s, null, null, '%s', null )
        """  % ( self.DB_NAME, self.TBL_CATALOG_REQUESTS, 
                 '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' ) 

        #client_id, user_id and checksum must be unique, to prevent duplicate queries
        self.cursor.execute( 
            query, ( 
                user_id, 
                client_id, 
                state,
                resource_name,
                redirect_uri,                
                expiry_time, 
                query_code,
                checksum,
                request_status,
                time.time() 
            ) 
        )

        self.commit()
    
        
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_request_by_id( self, request_id ) :

        if request_id :
            query = """
                SELECT t.*, s.* FROM %s.%s t
                JOIN %s.%s s ON s.resource_id = t.resource_id
                WHERE request_id = %s
            """  % ( 
                self.DB_NAME, self.TBL_CATALOG_REQUESTS, 
                self.DB_NAME, self.TBL_CATALOG_RESOURCES,'%s', )
                 
            self.cursor.execute( query, ( request_id, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None     
        

    #///////////////////////////////////////


    @safety_mysql                
    def fetch_request_by_auth_code( self, auth_code ) :

        if auth_code :
            query = """
                SELECT * FROM %s.%s t where auth_code = %s 
            """  % ( self.DB_NAME, self.TBL_CATALOG_REQUESTS, '%s' ) 
        
            self.cursor.execute( query, ( auth_code, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None     
              

    #///////////////////////////////////////


    @safety_mysql                
    def fetch_install_by_auth_code( self, auth_code ) :

        if auth_code :
            query = """
                SELECT * FROM %s.%s t where auth_code = %s 
            """  % ( self.DB_NAME, self.TBL_CATALOG_INSTALLS, '%s' ) 
        
            self.cursor.execute( query, ( auth_code, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None
        
                  
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_user_by_id( self, user_id ) :

        if user_id :
            query = """
                SELECT * FROM %s.%s t where user_id = %s 
            """  % ( self.DB_NAME, self.TBL_CATALOG_USERS, '%s' ) 
        
            self.cursor.execute( query, ( user_id, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None     
            
       
        
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_user_by_name( self, user_name ) :

        if user_name :
            query = """
                SELECT * FROM %s.%s t where user_name = %s 
            """  % ( self.DB_NAME, self.TBL_CATALOG_USERS, '%s' ) 
        
            self.cursor.execute( query, ( user_name, ) )
            row = self.cursor.fetchone()

            if not row is None:
                return row
            else :
                return None
        else :
            return None     
            
            
    #///////////////////////////////////////


    @safety_mysql                
    def fetch_user_by_email( self, email ) :

        if email :
            query = """
                SELECT * FROM %s.%s t where email = %s 
            """  % ( self.DB_NAME, self.TBL_CATALOG_USERS, '%s' ) 
        
            self.cursor.execute( query, ( email, ) )
            row = self.cursor.fetchone()
            if not row is None:
                return row
            else :
                return None    
        else :
            return None             

    
    #///////////////////////////////////////


    @safety_mysql                
    def update_request( self, request_id, request_status, access_token, auth_code ) :

        if request_id and access_token :
            query = """
                UPDATE %s.%s 
                SET request_status=%s, access_token = %s, auth_code = %s, ctime = %s
                where request_id = %s 
            """  % ( self.DB_NAME, self.TBL_CATALOG_REQUESTS, '%s', '%s', '%s', '%s', '%s' ) 
        
            update = self.cursor.execute( 
                query, 
                ( request_status, access_token, auth_code,  time.time(), request_id,) 
            )
            
            if update > 0 :
                log.debug( 
                    "%s: Access request %s registered with access_token %s" 
                    % ( self.name, request_id, access_token )  
                )
                return True
            else:
                log.warning( 
                    "%s: trying to update an unknown request %s" 
                    % (self.name, request_id ) 
                )
                return False
        else :
            log.warning( 
                "%s: attempting to update access request with insufficient parameters" 
                % self.name 
            )
            return False
      
        
    #///////////////////////////////////////


    @safety_mysql                
    def delete_request( self, request_id ) :

        if request_id :
            query = """
                DELETE FROM %s.%s WHERE request_id = %s 
            """  % ( self.DB_NAME, self.TBL_CATALOG_REQUESTS, '%s' ) 
        
            update = self.cursor.execute( query, ( request_id, ) )
            
            if update > 0 :
                log.debug( "%s: Access request %s deleted" % ( self.name, request_id ) )
                return True
            else:
                log.warning( "%s: trying to delete unknown request %s" % (self.name, request_id ) )
                return False
        else :
            log.warning( 
                "%s: attempting to delete an access request with insufficient parameters" 
                % self.name 
            )
            return False        


    #///////////////////////////////////////
       
              
    @safety_mysql                
    def insert_user( self, user_id ):
        
        if user_id:
            
            log.info( 
                "%s %s: Adding user '%s' into database" 
                % ( self.name, "insert_user", user_id ) 
            );
            
            query = """
                INSERT INTO %s.%s 
                ( user_id, user_name, email, registered ) 
                VALUES ( %s, null, null, null )
            """  % ( self.DB_NAME, self.TBL_CATALOG_USERS, '%s' ) 

            self.cursor.execute( query, ( user_id ) )
            return True;
        
        else:
            log.warning( 
                "%s %s: Was asked to add 'null' user to database" 
                % (  self.name, "insert_user", ) 
            );
            return False;

 
    #///////////////////////////////////////
    
    
    @safety_mysql                    
    def insert_registration( self, user_id, user_name, email ):
            
        if ( user_id and user_name and email ):
            
            log.info( 
                "%s %s: Updating user '%s' registration in database" 
                % ( self.name, "insert_registration", user_id ) 
            );
            
            query = """
                UPDATE %s.%s 
                SET user_name = %s, email = %s, registered= %s 
                WHERE user_id = %s
            """  % ( self.DB_NAME, self.TBL_CATALOG_USERS, '%s', '%s', '%s', '%s' ) 

            self.cursor.execute( query, ( user_name, email, time.time(), user_id ) )
            return True;
        
        else:
            log.warning( 
                "%s %s: Registration requested with incomplete details" 
                % (  self.name, "insert_registration", ) 
            );
            return False; 
        

    #///////////////////////////////////////
    
  
    @safety_mysql                
    def fetch_requests( self, user_id = None ):
      
        if user_id:
            
            query = """
                SELECT s.*, t.client_name, r.resource_name
                FROM %s.%s s, %s.%s t, %s.%s r
                WHERE s.user_id = %s 
                AND s.client_id = t.client_id
                AND s.resource_id = r.resource_id
            """ % ( 
                self.DB_NAME, self.TBL_CATALOG_REQUESTS, 
                self.DB_NAME, self.TBL_CATALOG_CLIENTS,
                self.DB_NAME, self.TBL_CATALOG_RESOURCES,  '%s' 
            )

            self.cursor.execute( query, ( user_id, ) )
            return self.cursor.fetchall()
        else:
            return None
        
        
                