'''    
Created on 12 April 2011
@author: jog
'''

import MySQLdb
import logging
import ConfigParser
from time import * #@UnusedWildImport
import sys

class PrefstoreDB( object ):
    ''' classdocs '''
    
    DB_NAME = 'prefstore'
    TBL_PERIODS = 'tblPeriods'
    TBL_TERM_APPEARANCES = 'tblTermAppearances'
    TBL_TERM_DICTIONARY = 'tblTermDictionary'
    TBL_TERM_BLACKLIST = 'tblTermBlacklist'
    TBL_USER_DETAILS = 'tblUserDetails'
    CONFIG_FILE = "prefstore.cfg"
    SECTION_NAME = "PrefstoreDB"


    #///////////////////////////////////////

 
    createQueries = { 
               
        TBL_TERM_DICTIONARY : """
            CREATE TABLE %s.%s (
            term varchar(128) NOT NULL,
            term_id int(10) unsigned NOT NULL AUTO_INCREMENT,
            mtime int(10) unsigned NOT NULL,
            count int(10) unsigned,
            ctime int(10) unsigned,
            PRIMARY KEY (term_id), UNIQUE KEY `UNIQUE` (`term`) )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_TERM_DICTIONARY ),
        
        TBL_TERM_BLACKLIST : """
            CREATE TABLE %s.%s (
            term varchar(128) NOT NULL,
            term_id int(10) unsigned NOT NULL AUTO_INCREMENT,
            PRIMARY KEY (term_id), UNIQUE KEY `UNIQUE` (`term`) )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_TERM_BLACKLIST ),
        
        TBL_TERM_APPEARANCES : """
            CREATE TABLE %s.%s (
            user_id varchar(256) NOT NULL,
            term varchar(128) NOT NULL,
            doc_appearances bigint(20) unsigned NOT NULL,
            total_appearances bigint(20) unsigned NOT NULL,
            last_seen int(10) unsigned NOT NULL,
            PRIMARY KEY (user_id, term),
            FOREIGN KEY (user_id) REFERENCES %s(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (term) REFERENCES %s(term) ON DELETE CASCADE ON UPDATE CASCADE )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
            
        """  % ( DB_NAME, TBL_TERM_APPEARANCES, TBL_USER_DETAILS, TBL_TERM_DICTIONARY ),
       
        TBL_USER_DETAILS : """
            CREATE TABLE %s.%s (
            user_id varchar(256) NOT NULL,
            screen_name varchar(64),
            email varchar(256),
            total_documents int(10) unsigned NOT NULL,
            last_distill int(10) unsigned NOT NULL,
            last_message int(10) unsigned NOT NULL,
            total_term_appearances bigint(20) NOT NULL DEFAULT 0,
            registered int(10) unsigned,            
            PRIMARY KEY (user_id) )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_USER_DETAILS ),   
    } 
    
    
    #///////////////////////////////////////
    
    
    def __init__( self, name = "PrefstoreDB" ):
            
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
        
        logging.info( "%s: connecting to mysql database..." % self.name )

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
        logging.info( "%s: Database reconnection process activated:" % self.name );
        self.close()
        self.connect()
        

    #///////////////////////////////////////
          
                
    def commit( self ) : 
        self.conn.commit();
        
        
    #///////////////////////////////////////
        
          
    def close( self ) :
        
        logging.info( "%s: disconnecting from mysql database..." % self.name );
        self.cursor.close();
        self.conn.close()
                     
                            
    #////////////////////////////////////////////////////////////////////////////////////////////
    
    
    def check_tables( self ):
        
        logging.info( "%s: checking system table integrity..." % self.name );
        
        self.cursor.execute ( """
            SELECT table_name
            FROM information_schema.`TABLES`
            WHERE table_schema='%s'
        """ % self.DB_NAME )
        
        tables = [ row[ "table_name" ] for row in self.cursor.fetchall() ]
 
        if not self.TBL_USER_DETAILS in tables : 
            self.create_table( self.TBL_USER_DETAILS )
        if not self.TBL_TERM_DICTIONARY in tables : 
            self.create_table( self.TBL_TERM_DICTIONARY )   
        if not self.TBL_TERM_BLACKLIST in tables : 
            self.create_table( self.TBL_TERM_BLACKLIST )                      
        if not self.TBL_TERM_APPEARANCES in tables : 
            self.create_table( self.TBL_TERM_APPEARANCES )
     
        self.commit();
        
        
    #///////////////////////////////////////
    
               
    def create_table( self, tableName ):
        logging.warning( 
            "%s: missing system table detected: '%s'" 
            % ( self.name, tableName ) 
        );
        
        if tableName in self.createQueries :
            
            logging.info( 
                "%s: --- creating system table '%s' " 
                % ( self.name, tableName )
            );  
              
            self.cursor.execute( self.createQueries[ tableName ] )


    #///////////////////////////////////////
              
                
    def insert_user( self, user_id ):
        
        if user_id:
            
            logging.info( 
                "%s %s: Adding user '%s' into database" 
                % ( self.name, "insert_user", user_id ) 
            );
            
            query = """
                INSERT INTO %s.%s 
                ( user_id, screen_name, email, total_documents, last_distill, last_message, total_term_appearances, registered ) 
                VALUES ( %s, null, null, 0, 0, 0, 0, null )
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s' ) 

            self.cursor.execute( query, ( user_id ) )
            return True;
        
        else:
            logging.warning( 
                "%s %s: Was asked to add 'null' user to database" 
                % (  self.name, "insert_user", ) 
            );
            return False;

 
    #///////////////////////////////////////
    
    
    def insert_registration( self, user_id, screen_name, email ):
            
        if ( user_id and screen_name and email ):
            
            logging.info( 
                "%s %s: Updating user '%s' registration in database" 
                % ( self.name, "insert_registration", user_id ) 
            );
            
            query = """
                UPDATE %s.%s 
                SET screen_name = %s, email = %s, registered= %s 
                WHERE user_id = %s
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', '%s', '%s', '%s' ) 

            self.cursor.execute( query, ( screen_name, email, time(), user_id ) )
            return True;
        
        else:
            logging.warning( 
                "%s %s: Registration requested with incomplete details" 
                % (  self.name, "insert_registration", ) 
            );
            return False;    

            
    #///////////////////////////////////////


    def fetch_user_by_id( self, user_id ) :

        if user_id :
            query = """
                SELECT * FROM %s.%s t where user_id = %s 
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s' ) 
        
            self.cursor.execute( query, ( user_id, ) )
            row = self.cursor.fetchone()
            if not row is None:
                return row
            else :
                return None
        else :
            return None     
            
            
    #///////////////////////////////////////


    def fetch_user_by_email( self, email ) :

        if email :
            query = """
                SELECT * FROM %s.%s t where email = %s 
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s' ) 
        
            self.cursor.execute( query, ( email, ) )
            row = self.cursor.fetchone()
            if not row is None:
                return row
            else :
                return None    
        else :
            return None     
        
        
    #///////////////////////////////////////
                    
                    
    def incrementUserInfo(self, 
            user_id = None, 
            total_term_appearances = 1, 
            mtime = None ) :

        if user_id and mtime:
  
            query = """
                UPDATE %s.%s 
                SET total_documents = total_documents + 1, 
                    total_term_appearances = total_term_appearances + %s,
                    last_distill = %s,
                    last_message = %s
                WHERE user_id = %s
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', '%s', '%s', '%s' )
            
            update = self.cursor.execute( 
                query, ( total_term_appearances, mtime, int( time() ), user_id ) )

            if update > 0 :
                logging.debug( 
                    "%s: Updated user info for %s" 
                    % ( self.name, user_id )  
                )
                return True
            else:
                logging.warning( 
                    "%s: trying to update an unknown user" 
                    % self.name 
                )
                return False
        else :
            logging.warning( 
                "%s: attempting to update User with incomplete data" 
                % self.name 
            )
            return False
        
        
        
    #//////////////////////////////////////////////////////////
    # WEB UPDATER CALLS
    #//////////////////////////////////////////////////////////               
        
        
    def getMissingCounts( self ):
       
        query = """
            SELECT term FROM %s.%s where count IS NULL 
        """  % ( self.DB_NAME, self.TBL_TERM_DICTIONARY ) 
        self.cursor.execute( query  )
        resultSet = [ row[ 'term' ] for row in self.cursor.fetchall() ]
        return resultSet
    
    
    #///////////////////////////////////////
                   
        
    def updateTermCount( self, term, count ):
        
        if term: 
            query = "UPDATE %s.%s SET count = %s, ctime = %s WHERE term = %s" % \
                ( self.DB_NAME, self.TBL_TERM_DICTIONARY, '%s', '%s', '%s' ) 
            
            logging.debug( 
                "%s %s: Updating dictionary term '%s' with web count '%d'" 
                % ( self.name, "updateTermCount", term, count ) 
            );
            
            self.cursor.execute( query, ( count, time(), term )  )
            
            return True
        else:
            return False
   
    
    #///////////////////////////////////////   
    
    
    def insertDictionaryTerm( self, term = None ):

        try:     
            if term:
                logging.debug( 
                    "%s %s: Creating new dictionary term '%s' " 
                    % ( self.name, "insertDictionaryTerm", term ) 
                );
                
                query = """
                    INSERT INTO %s.%s ( term, mtime, count, ctime ) 
                    VALUES ( %s, %s, null, null )
                """  % ( self.DB_NAME, self.TBL_TERM_DICTIONARY, '%s', '%s' ) 
               
                self.cursor.execute( query, ( term, int( time() ) ) )
                
            else:
                logging.warning(
                    "%s %s: Trying to create new dictionary term '%s' : ignoring..." 
                    % ( self.name, "insertDictionaryTerm", term ) 
                );
                     
        except:
            logging.error( "error %s" % sys.exc_info()[0] )

             
    #///////////////////////////////////////
            
    
    def deleteDictionaryTerm( self, term = None ):
        
        logging.debug( 
            "%s %s: Deleting term '%s' " 
            % ( self.name, "deleteDictionaryTerm", term ) 
        );
        
        query = "DELETE FROM %s.%s WHERE term = %s"  % ( self.DB_NAME, self.TBL_TERM_DICTIONARY, '%s' ) 
        self.cursor.execute( query, ( term ) )

                  
    #///////////////////////////////////////
              
                
    def updateTermAppearance( self, user_id = None, term = None, freq = 0 ):
        
        try:
            if term and user_id:
                
                logging.debug( 
                    "%s %s: Updating term '%s' for user '%s': +%d appearances" 
                    % ( self.name, "updateTermAppearance", term, user_id, freq ) 
                );
                query = """
                    INSERT INTO %s.%s ( user_id, term, doc_appearances, total_appearances, last_seen ) 
                    VALUES ( %s, %s, %s, %s, %s )
                    ON DUPLICATE KEY UPDATE 
                    doc_appearances = doc_appearances + 1, 
                    total_appearances = total_appearances + %s,
                    last_seen = %s
                """  % ( self.DB_NAME, self.TBL_TERM_APPEARANCES, '%s', '%s', '%s', '%s', '%s', '%s', '%s' )
                
                self.cursor.execute( query, ( user_id, term, 1, freq, int( time() ), freq, int( time() ) ) )
                  
            else:
                logging.warning( 
                    "%s %s: Updating term '%s' for user '%s': ignoring..." 
                    % ( self.name, "updateTermAppearance" , term, user_id, freq ) 
                );
            
        except Exception, e:
            logging.error(
                "%s %s: error %s" 
                % ( self.name, "updateTermAppearance" , sys.exc_info()[0] ) 
            )

        
    #///////////////////////////////////////             
              
              
    def getTermAppearance( self, user_id, term ):
        
        if user_id and term :
            query = """
                SELECT * FROM %s.%s t where user_id = %s and term = %s 
            """  % ( self.DB_NAME, self.TBL_TERM_APPEARANCES, '%s', '%s' ) 
        
            self.cursor.execute( query, ( user_id, term ) )
            row = self.cursor.fetchone()
            if not row is None:
                return row
            else :
                return None
    
            
    #///////////////////////////////////////          
    
        
    def getTermCount( self, term = None ):
        
        if term:
            
            query = "SELECT count FROM %s.%s WHERE term = %s"  \
                % ( self.DB_NAME, self.TBL_TERM_DICTIONARY, '%s' ) 

            self.cursor.execute( query, ( term, ) )
 
            row = self.cursor.fetchone()
            if row == None : 
                return None
            else :
                return row[ 'count' ]
        else:
            return None
          
    
    #///////////////////////////////////////          


    def getTermCountList( self, fv = None ):
         
        if fv:
            #convert terms into an appropriate escape string
            formatStrings = ','.join( ['%s'] * len( fv ) )
            query = "SELECT term, count FROM %s.%s where term IN (%s)" % \
                (  self.DB_NAME, self.TBL_TERM_DICTIONARY, formatStrings )
                
            #get the web counts from the db for those terms
            self.cursor.execute( query, tuple( fv ) )
            
            #convert those results into a dictionary and return it
            return dict( [ ( row.get( 'term' ), row.get( 'count' ) ) for row in self.cursor.fetchall() ] )
        else:
            return None          
    
    
    #///////////////////////////////////////          


    def matchExistingTerms( self, terms = None ):
        
        """
            Takes an array of terms and removes those that have not
            already been seen before, and are hence recorded in the db. 
            The result is returned as a list - which could well be empty.
        """
        if terms:
            #convert terms into an appropriate escape string
            formatStrings = ','.join( ['%s'] * len( terms ) )
            query = "SELECT term FROM %s.%s where term IN (%s)" % \
                (  self.DB_NAME, self.TBL_TERM_DICTIONARY, formatStrings )
                
            #get the web counts from the db for those terms
            self.cursor.execute( query, tuple( terms ) )
            
            #convert those results into a dictionary and return it
            return [ row.get( 'term' ) for row in self.cursor.fetchall() ] 
        else:
            return []
        
            
    #///////////////////////////////////////          


    def removeBlackListed( self, terms = None ):
        """
            Takes an array of terms and removes those in it that are 
            recorded in the databases blacklisted words. Returns the 
            result as a list - which could well be empty.
        """
        if terms:
            #convert terms into an appropriate escape string
            formatStrings = ','.join( ['%s'] * len( terms ) )
            
            query = "SELECT term FROM %s.%s where term IN (%s)" % \
                ( self.DB_NAME, self.TBL_TERM_BLACKLIST, formatStrings )
                
            #get the web counts from the db for those terms
            self.cursor.execute( query, tuple( terms ) )
            
            #convert those results into a dictionary and return it
            matches = [ row.get( 'term' ) for row in self.cursor.fetchall() ]
            
            logging.debug( 
                "%s %s: Removing %d terms from distillation" 
                % ( self.name, "removeBlackListed", len( matches ) ) 
            );
            
            return [ term for term in terms if term not in matches ]
        else:
            return []
        
        
    #///////////////////////////////////////
       
       
    def blacklistTerm( self, term ):           
        logging.info( "Blacklisting term '%s' " % ( term ) );
        self.deleteDictionaryTerm( term )
        
        try:     
            if term:
                logging.debug( 
                    "%s %s: Blocking new  term '%s' " 
                    % ( self.name, "blacklistTerm", term ) 
                );
                
                query = """
                    INSERT INTO %s.%s ( term ) 
                    VALUES ( %s )
                """  % ( self.DB_NAME, self.TBL_TERM_BLACKLIST, '%s' ) 
                
                self.cursor.execute( query, ( term ) )
                
            else:
                logging.debug( 
                    "%s %s: Blocking new term '%s' : ignoring..." 
                    % ( self.name, "blacklistTerm", term ) 
                )
                     
        except:
            logging.error( 
                "%s %s: Error %s" 
                % ( self.name, "blacklistTerm",sys.exc_info()[0] ) 
            )


    #///////////////////////////////////////


    def fetch_terms( self, 
        user_id, 
        order_by='total appearances',
        direction='DESC',
        LIMIT=1000,
        MIN_WEB_PREVALENCE=10000,
        TOTAL_WEB_DOCUMENTS=25000000000
    ) :
        FIELDS = { 
            "alphabetical order":"term", 
            "total appearances":"total_appearances", 
            "doc appearances":"doc_appearances",
            "frequency":"total_appearances", 
            "web importance":"count",
            "relevance":"weight",
            "last seen":"last_seen",
        }
        
        if user_id and order_by in FIELDS.keys():

            query = """
                SELECT 
                    t.*, 
                    d.count,
                    ( t.total_appearances  / (d.count / %d ) ) weight  
                FROM %s.%s t, %s.%s d 
                WHERE user_id = %s
                AND t.term = d.term
                AND d.count > %d
                ORDER BY %s %s
                LIMIT %s
            """  % ( 
                TOTAL_WEB_DOCUMENTS,
                self.DB_NAME, self.TBL_TERM_APPEARANCES, 
                self.DB_NAME, self.TBL_TERM_DICTIONARY,
                '%s', 
                MIN_WEB_PREVALENCE, 
                FIELDS[ order_by ], 
                direction, 
                '%s' ) 
            
            self.cursor.execute( query, ( user_id, LIMIT ) )
            results = self.cursor.fetchall()
            
            if not results is None:
                return results
            else :
                return {}
        else :
            return {}     
        
        
    #///////////////////////////////////////


    def search_terms( self, 
        user_id, 
        search_term,
        match_type="exact" ) :
        
        MATCH_TYPES = {
            "exact":"t.term = '%s'" % ( search_term, ),
            "starts":"t.term LIKE '%s'" % (  search_term + "%%", ),
            "contains":"t.term LIKE '%s'" % ( "%%" + search_term + "%%", ), 
            "ends":"t.term LIKE '%s'" % ( "%%" + search_term, ),             
        }
        
        LIMIT = 500
        
        if user_id and search_term and match_type in MATCH_TYPES.keys():
            
            query = """
                SELECT t.*, d.count FROM %s.%s t, %s.%s d 
                WHERE user_id = %s
                AND t.term = d.term
                AND %s
                ORDER BY t.term
                LIMIT %s
            """  % ( 
                self.DB_NAME, self.TBL_TERM_APPEARANCES, 
                self.DB_NAME, self.TBL_TERM_DICTIONARY,
                '%s', MATCH_TYPES[ match_type ], LIMIT ) 

            self.cursor.execute( query, ( user_id ) )
            results = self.cursor.fetchall()
            
            if not results is None:
                return results
            else :
                return {}
        else :
            return {}    