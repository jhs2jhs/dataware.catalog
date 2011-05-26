"""
Created on 12 April 2011
@author: jog
"""

import validictory
from webcountupdater import * #@UnusedWildImport
from prefstoredb import * #@UnusedWildImport
from bottle import * #@UnusedWildImport


schema = {
    "type" : "object",
        "properties" : {
            "user" : {
                "type" : "string",
                "minLength" : 3 
            },
            "docId" : {
                "type" : "string",  
                "minLength" : 3 
            },
            "docType" :  {
                "type" : "string",
                "minLength" : 3
            },
            "docName" :  {
                "type" : "string",
                "minLength" : 0
            },
            "appName" : {
                "type" : "string",
                "minLength" : 3
            },
            "totalWords" : {
                "type" : "integer" 
            },
            "duration" : {
                "type" : "integer" 
            },
            "mtime" : {
                "type" : "integer" 
            },
            "key" : {
                "type" : "string" 
            },            
            "fv" : {
                "type" : "object",
                "patternProperties": { ".*": { "type": "integer" } } 
            }      
        }
    }   

    
#///////////////////////////////////////////////


def main(): 
                   
    logging.basicConfig( 
        format= '%(asctime)s [%(levelname)s] %(message)s', 
        datefmt='%Y-%m-%d %I:%M:%S',
        filename='logs/prefstore.log',
        level=logging.DEBUG 
    )
    
    try:
        global db;    
        db = prefstoredb()  
        db.connect()  
        db.checkTables()

        updater = webcountupdater()
        updater.start()
        
        logging.info( 
            "database initialisation completed... [SUCCESS]"
        );
                
        debug(True)
        run( host='0.0.0.0', port=8080 )
        
    except ValueError, e:
        logging.error( 
            "%s: Error %d: %s" 
            % ( "prefstore", e.args[0], e.args[1] ) 
        )
        
    except:
        logging.error( 
            "%s: Uncaught error %s" 
            % ( "prefstore", sys.exc_info()[0] ) 
        )      
        
    db.close();    


#///////////////////////////////////////////////


def safetyCall( func ):
    """
        This is a function that protects from mysqldb timeout,
        performing one reconnection attempt if the provided lambda 
        function generates a mysqldb error. This is necessary because
        mysqldb does not currently provided an auto_reconnect facility.
    """
    try:
        return func();
    except MySQLdb.Error, e:
        logging.error( "%s: db error %s" % ( "prefstore", e.args[ 0 ] ) )
        db.reconnect()
        return func();
    
    
#///////////////////////////////////////////////


@route( '/ping')
def ping():
    return "pong"
    

#///////////////////////////////////////////////


@route( '/login', method = "POST")
def login():
    
    try:
        data = json.loads( request.forms.get( 'data' ) )
        user = data.get( 'user' )
        password = data.get( 'pass' )

        try:
            # First db interaction of this method so safety check in case 
            # a mysql timeout has occurred since we last accessed the db.
            key = safetyCall( lambda: 
                db.checkLogin( user, password ) 
            )
            
            #commit occurs because a new key is generated when Login is checked.
            db.commit()
            
            if ( key  ):

                logging.info( 
                    "%s: Logging in user '%s'... [SUCCESS]"
                    % ( "prefstore", user )
                );                
                return "{'success':true,'key':'%s'}" % key
            else:
                logging.info( 
                    "%s: Logging in user '%s'... [FAILED]" 
                    % ( "prefstore", user ) 
                );
                return "{'success':false, 'error':'unknown user/pass'}"
            
        except:
            logging.error( 
                "%s: login database error - %s "
                % ( "prefstore", sys.exc_info()[0] )
            )
            return "{'success':false, 'error':'database error'}"
    except:
        return "{'success':false, 'error':'JSON error'}"
    

#///////////////////////////////////////////////


@route( '/newUser', method = "POST")
def newUser():
    
    #load in the necessary data to create the new user.
    try:
        data = json.loads( request.forms.get( 'data' ) )
        user = data.get( 'user' )
        password = data.get( 'pass' )
    except:
        logging.info( 
            "%s: Creating new user '%s'... error extracting post data [FAILED]"
            % ( "prefstore", user )
        );         
        return "{'success':false, 'error':'JSON error'}"
    
    #determine the acceptability of a supplied username
    #should it be a valid datasphere (i.e. xmpp) address?
    
    #insert the user into the database and respond successfully
    try:
        # First db interaction of this method so safety check in case 
        # a mysql timeout has occurred since we last accessed the db
        userInserted = safetyCall( lambda: 
            db.insertUser( user, password ) 
        )
        
        if not userInserted:
            return "{'success':false,'error':'incomplete details'}"
        
        key = db.createNewUserKey( user )
        db.commit()
        logging.info( 
            "%s: Creating new user '%s'... [SUCCESS]"
            % ( "prefstore", user )
        );   
        return "{'success':true,'key':'%s'}" % key
     
    #if the user already exists as a primary key an Integrity Error will be thrown
    except MySQLdb.IntegrityError:
        logging.info( 
            "%s: Creating new user '%s'... user already exists [FAILED]"
            % ( "prefstore", user )
        ); 
        return "{'success':false, 'error':'user already exists'}"

    #otherwise we have met some other (probably database) error    
    except:
        logging.info( 
            "%s: Creating new user '%s'... unknown error [FAILED]"
            % ( "prefstore", user )
        ); 
    
    return "{'success':false, 'error':'unknown error'}"    
            

#///////////////////////////////////////////////


@route( '/submitDistill', method = "POST" )
def submitDistill():
    """ 
        A Distillation is packaged as a json message of the form
        {user:u, docid:d, docType:t, appName:a, duration:d, mtime:m, fv:{ word:freq } }    
    """

    try:
        # First turn the json packet into a dictionary.
        data = json.loads( request.forms.get( 'data' ) )
        
        # Make sure the message is in the correct distill format.
        validictory.validate( data, schema )

        user = data.get( 'user' )
        key = data.get( 'key' )
        
        # Log that we have received the distill message.
        logging.info( 
            "%s: Message from '%s' successfully unpacked" 
            % ( "prefstore", user ) 
        )
        
        # First db interaction of this method so safety check in case 
        # a mysql timeout has occurred since we last accessed the db.
        authenticated = safetyCall( lambda: 
            db.authenticate( user, key )
        )
        
        # Authenticate the user, using the supplied key
        if authenticated:
            
            logging.debug( 
                "%s: Message from '%s' successfully authenticated" 
                % ( "prefstore", user  ) 
            )

            # And finally process it into the database
            if processDistill( data ):
                return "{'success':true }"
            else:
                logging.info( 
                    "%s: Message from '%s' failed processing" 
                    % ( "prefstore", user )
                ) 
                return "{'success':false,'cause':'processing error'}"
        
        else:
            logging.warning( 
                "%s: Message from '%s' failed authentication" 
                % ( "prefstore", user ) 
            )
            
            return "{'success':false,'cause':'authentication error'}"
        
    except ValueError, e:
        logging.error( 
            "%s: JSON validation error - %s" 
            % ( "prefstore", e ) 
        )          
        return "{'success':false,'cause':'JSON error'}"

    except MySQLdb.Error, e:
        logging.error( 
            "%s: Database error %s" 
            % ( "prefstore", e ) 
        )
        
        
        print "Error %d: %s" % (e.args[0], e.args[1])
        return "{'success':false,'cause':'Database error'}"
    
    return "{'success':false,'cause':'Unknown error'}"
    
    

    
#///////////////////////////////////////////////        
       
        
def processDistill( data ) :
    
    #Extract entry information
    user = data.get( 'user' )
    mtime = data.get( 'mtime' )
    fv = data.get( 'fv' )
    
    #Update user info, incrementing the number of documents we have received.
    userUpdated = db.incrementUserInfo( user, mtime )
    
    if not userUpdated :
        logging.error( 
            "%s: User '%s' could not be updated. Ignoring." 
            % ( "prefstore", user ) 
        )
        return False    

    #Split the terms into ones that exist in the db, and ones that don't
    terms = db.removeBlackListed( [ term for term in fv ] )
    existingTerms = db.matchExistingTerms( terms )
    newTerms = [ term for term in terms if term not in existingTerms ]
    processedTerms = 0

    #Process the terms we haven't seen before
    for term in newTerms:
        try:
            db.insertDictionaryTerm( term )
            db.insertTermAppearance( user, term, fv.get( term ) )
            processedTerms += 1
        except:
            logging.warning( 
                "%s: Failed to add term '%s' for '%s'" 
                % ( "prefstore", term, user ) 
            )

    #Process the terms that already exist in the dictinoary            
    for term in existingTerms:
        try:
            db.incrementTermAppearance( user, term, fv.get( term ) );    
            processedTerms += 1
        except:
            logging.warning( 
                "%s: Failed to increment term '%s' for '%s'" 
                % ( "prefstore", term, user ) 
            )
            
    #Everything seems okay, so commit the transaction
    db.commit()
    
    #Log the distillation results
    logging.info( 
        "%s: Message from '%s' (%d terms, %d extant, %d new, %d processed)" 
        % ( "prefstore", user, len( terms ), len( existingTerms ), len( newTerms ), processedTerms ) 
    )
    
    #And return from the function successfully
    return True
        


#///////////////////////////////////////////////


if __name__ == '__main__' :main()

   
    
