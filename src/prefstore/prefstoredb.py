'''    
Created on 12 April 2011
@author: jog
'''

import MySQLdb
import logging
import sys
import base64
import hashlib
import random
from time import time
import ConfigParser

class prefstoredb( object ):
    ''' classdocs '''
    
    DB_NAME = 'prefstore'
    TBL_PERIODS = 'tblPeriods'
    TBL_TERM_APPEARANCES = 'tblTermAppearances'
    TBL_TERM_DICTIONARY = 'tblTermDictionary'
    TBL_TERM_BLACKLIST = 'tblTermBlacklist'
    TBL_USER_DETAILS = 'tblUserDetails'
    CONFIG_FILE = "prefstore.ini"
    SECTION_NAME = "prefstoredb"
    
    #///////////////////////////////////////
    
    
    createQueries = { 
               
        TBL_TERM_DICTIONARY : """
            CREATE TABLE %s.%s (
            term varchar(128) NOT NULL,
            termId int(10) unsigned NOT NULL AUTO_INCREMENT,
            mtime int(10) unsigned NOT NULL,
            count int(10) unsigned,
            ctime int(10) unsigned,
            PRIMARY KEY (termId), UNIQUE KEY `UNIQUE` (`term`) )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_TERM_DICTIONARY ),
        
        TBL_TERM_BLACKLIST : """
            CREATE TABLE %s.%s (
            term varchar(128) NOT NULL,
            termId int(10) unsigned NOT NULL AUTO_INCREMENT,
            PRIMARY KEY (termId), UNIQUE KEY `UNIQUE` (`term`) )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_TERM_BLACKLIST ),
        
        TBL_TERM_APPEARANCES : """
            CREATE TABLE %s.%s (
            user varchar(256) NOT NULL,
            term varchar(128) NOT NULL,
            docAppearances bigint(20) unsigned NOT NULL,
            totalAppearances bigint(20) unsigned NOT NULL,
            PRIMARY KEY (user, term),
            FOREIGN KEY (user) REFERENCES %s(user) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (term) REFERENCES %s(term) ON DELETE CASCADE ON UPDATE CASCADE )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
            
        """  % ( DB_NAME, TBL_TERM_APPEARANCES, TBL_USER_DETAILS, TBL_TERM_DICTIONARY ),
       
        TBL_USER_DETAILS : """
            CREATE TABLE %s.%s (
            user varchar(256) NOT NULL,
            totalDocuments int(10) unsigned NOT NULL,
            lastDistill int(10) unsigned NOT NULL,
            lastMessage int(10) unsigned NOT NULL,
            password varchar(128) NOT NULL,
            currentKey varchar(256) DEFAULT NULL,
            PRIMARY KEY (user) )
            ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """  % ( DB_NAME, TBL_USER_DETAILS ),   
    } 
    

    #///////////////////////////////////////
    
    
    def __init__( self, name = "prefstoredb" ):
            
        #MysqlDb is not thread safe, so program may run more
        #than one connection. As such naming them is useful.
        self.name = name
        
        Config = ConfigParser.ConfigParser()
        Config.read( self.CONFIG_FILE )
        self.hostname = Config.get( self.SECTION_NAME, "hostname" )
        self.username =  Config.get( self.SECTION_NAME, "username" )
        self.password =  Config.get( self.SECTION_NAME, "password" )
        self.dbname = Config.get( self.SECTION_NAME, "dbname" )

        
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
                     
                            
    #///////////////////////////////////////
    
    
    def authenticate( self, user, key ) :
        
        if user and key:
            query = """
                SELECT 1 FROM %s.%s WHERE user = %s AND currentKey = %s  
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', '%s' ) 

            self.cursor.execute( query, ( user, key ) )
            row = self.cursor.fetchone()

            if ( row is None ):
                return False
            else:    
                return True
        else:    
            return False



    #///////////////////////////////////////
    
        
    def checkTables( self ):
        
        logging.info( "%s: checking system table integrity..." % self.name );
        
        self.cursor.execute ( """
            SELECT table_name
            FROM information_schema.`TABLES`
            WHERE table_schema='%s'
        """ % self.DB_NAME )
        
        tables = [ row[ "table_name" ] for row in self.cursor.fetchall() ]
 
        if not self.TBL_USER_DETAILS in tables : 
            self.createTable( self.TBL_USER_DETAILS )
        if not self.TBL_TERM_DICTIONARY in tables : 
            self.createTable( self.TBL_TERM_DICTIONARY )   
        if not self.TBL_TERM_BLACKLIST in tables : 
            self.createTable( self.TBL_TERM_BLACKLIST )                      
        if not self.TBL_TERM_APPEARANCES in tables : 
            self.createTable( self.TBL_TERM_APPEARANCES )
     
        self.commit();
        
        
    #///////////////////////////////////////
    
               
    def createTable( self, tableName ):
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
              
                
    #TODO: WHAT HAPPENS IF USER ALREADY EXISTS!?
    def insertUser( self, user = None, password = None ):
        
        if password and user:
            
            logging.info( 
                "%s %s: Adding user '%s' into database" 
                % ( self.name, "insertUser", user ) 
            );
            
            query = """
                INSERT INTO %s.%s 
                ( user, totalDocuments, lastDistill, lastMessage, password, currentKey ) 
                VALUES ( %s, 0, 0, 0, %s, null )
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', '%s' ) 

            self.cursor.execute( query, ( user, password ) )
            return True;
        
        else:
            logging.warning( 
                "%s %s: Adding user '%s' with pass '%s': ignoring..." 
                % (  self.name, "insertUser", user, password ) 
            );
            return False;
 

    #///////////////////////////////////////
       
       
    def checkLogin( self, user, password ):           
        
        if user:
            query = """
                SELECT password FROM %s.%s where user = %s  
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', ) 
        
            self.cursor.execute( query, ( user, ) )
            row = self.cursor.fetchone()

            if ( row is None ):
                return None
            
            if ( password == row.get( "password" ) ):
                key = self.createNewUserKey( user )
                return key 
            else:    
                return None
        else:    
            return None
 
 
    #///////////////////////////////////////
              
                
    def createNewUserKey( self, user = None):
        
        if ( user ):
            key = base64.b64encode(  
                    hashlib.sha256( 
                        str( random.getrandbits(256) ) 
                    ).digest() 
                )  
            
            #replace plus signs with asterisks. Plus signs are reserved
            #characters in ajax transmissions, so just cause problems
            key = key.replace( '+', '*' ) 
                
            query = "UPDATE %s.%s SET currentKey = %s WHERE user = %s" \
                % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', '%s' )  
            
            self.cursor.execute( query, ( key, user ) )
            return key
        

    #///////////////////////////////////////
                    
                    
    def incrementUserInfo(self, user = None, mtime = None ) :
        
        if user and mtime:
            
            query = """
                UPDATE %s.%s 
                SET totalDocuments = totalDocuments + 1, 
                    lastDistill = %s,
                    lastMessage = %s
                WHERE user = %s
            """  % ( self.DB_NAME, self.TBL_USER_DETAILS, '%s', '%s', '%s' )
            
            update = self.cursor.execute( query, ( mtime, int( time() ), user ) )

            if update > 0 :
                logging.debug( 
                    "%s: Updated user info for %s" 
                    % ( self.name, user )  
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
              
                
    def updateTermAppearance( self, user = None, term = None, freq = 0 ):
        
        try:
            if term and user:
                
                logging.debug( 
                    "%s %s: Updating term '%s' for user '%s': +%d appearances" 
                    % ( self.name, "updateTermAppearance", term, user, freq ) 
                );
                
                query = """
                    INSERT INTO %s.%s ( user, term, docAppearances, totalAppearances ) 
                    VALUES ( %s, %s, %s, %s )
                    ON DUPLICATE KEY UPDATE 
                    docAppearances = docAppearances + 1, 
                    totalAppearances = totalAppearances + %s
                """  % ( self.DB_NAME, self.TBL_TERM_APPEARANCES, '%s', '%s', '%s', '%s', '%s' )

                self.cursor.execute( query, ( user, term, 1, freq, freq ) )
                
            else:
                logging.warning( 
                    "%s %s: Updating term '%s' for user '%s': ignoring..." 
                    % ( self.name, "updateTermAppearance" , term, user, freq ) 
                );
            
        except:
            logging.error(
                "%s %s: error %s" 
                % ( self.name, "updateTermAppearance" , sys.exc_info()[0] ) 
            )

        
    #///////////////////////////////////////             
              
              
    def getTermAppearance( self, user, term ):
        
        if user and term :
            query = """
                SELECT * FROM %s.%s t where user = %s and term = %s 
            """  % ( self.DB_NAME, self.TBL_TERM_APPEARANCES, '%s', '%s' ) 
        
            self.cursor.execute( query, ( user, term ) )
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


