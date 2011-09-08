"""
Created on 12 April 2011
@author: jog
"""

import logging
import json
import OpenIDManager
import ProcessingModule
import PrefstoreDB
from bottle import * #@UnusedWildImport
from WebCountUpdater import * #@UnusedWildImport
import MySQLdb
import validictory


#//////////////////////////////////////////////////////////
# DATAWARE WEB-API CALLS
#//////////////////////////////////////////////////////////
 
@route( '/invoke_request', method = "POST")
def invoke_request():
    
    try:
        access_token = request.forms.get( 'access_token' )
        jsonParams = request.forms.get( 'parameters' )
        result = pm.invoke_request( 
            access_token, 
            jsonParams 
        )

        return result
    
    except Exception, e:
        raise e
     

#///////////////////////////////////////////////
 
 
@route( '/permit_request', method = "POST" )
def permit_request():

    #TODO: Worth checking why this takes so long to parse
    #TODO: the input parameters into the request.forms object.
    #TODO: Long post parameters (queries) are taking ages.   
    try:
        user_id = request.forms.get( 'user_id' )
        catalog_secret = request.forms.get( 'catalog_secret' )
        client_id = request.forms.get( 'client_id' )
        jsonScope = request.forms.get( 'scope' )
        result = pm.permit_request( 
            catalog_secret, 
            client_id,  
            user_id, 
            jsonScope 
        )
        
        #the result, if successful, will include an access_code
        return result
    
    except Exception, e:
        raise e
          

#///////////////////////////////////////////////
 
 
@route( '/revoke_request', method = "POST")
def revoke_request():
    
    try:
        access_token = request.forms.get( 'access_token' )
        catalog_secret = request.forms.get( 'catalog_secret' )
        user_id = request.forms.get( 'user_id' )

        result = pm.revoke_request( 
            user_id,
            catalog_secret,
            access_token, 
        )
        
        return result
    
    except Exception, e:
        raise e


    
#//////////////////////////////////////////////////////////
# OPENID SPECIFIC WEB-API CALLS
#//////////////////////////////////////////////////////////


@route( '/login', method = "GET" )
def openIDlogin():

    try: 
        username = request.GET[ 'username' ]
    except: 
        username = None
    
    try: 
        provider = request.GET[ 'provider' ]
    except: 
        return error( "provider must be supplied" )
    
    url = OpenIDManager.process(
        realm=REALM,
        return_to=REALM + "/checkauth",
        provider=provider,
        username=username
    )
    
    redirect( url )


#///////////////////////////////////////////////

 
@route( "/checkauth", method = "GET" )
def authenticate():
    
    o = OpenIDManager.Response( request.GET )
    
    #check to see if the user logged in succesfully
    if ( o.is_success() ):
        
        user_id = o.get_user_id()
         
        #if so check we received a viable claimed_id
        if user_id:
            
            try:
                user = prefdb.fetch_user_by_id( user_id )
                
                #if this is a new user add them
                if ( not user ):
                    prefdb.insert_user( o.get_user_id() )
                    prefdb.commit()
                    screen_name = None
                else :
                    screen_name = user[ "screen_name" ]
                
                #if they have no "screen_name" it means that they
                #haven't registered an account yet    
                if ( not screen_name ):
                    json = '{"user_id":"%s","screen_name":null}' \
                        % ( user_id, )
                    
                else:
                    json = '{"user_id":"%s","screen_name":"%s"}' \
                        % ( user_id, user[ "screen_name" ] )
                     
                response.set_cookie( EXTENSION_COOKIE, json )
            
            except Exception, e:
                return error( e )
            
            
        #if they don't something has gone horribly wrong, so mop up
        else:
            delete_authentication_cookie()

    #else make sure the user is still logged out
    else:
        delete_authentication_cookie()
        
    redirect( ROOT_PAGE )

    
#///////////////////////////////////////////////


@route('/logout')
def logout():
    delete_authentication_cookie()
    redirect( ROOT_PAGE )
    
        
#///////////////////////////////////////////////
 
         
def delete_authentication_cookie():
    response.set_cookie( 
        key=EXTENSION_COOKIE,
        value='',
        max_age=-1,
        expires=0
    )
            

#//////////////////////////////////////////////////////////
# PREFSTORE SPECIFIC WEB-API CALLS
#//////////////////////////////////////////////////////////


class LoginException ( Exception ):
    def __init__(self, msg):
        self.msg = msg


#///////////////////////////////////////////////  


class RegisterException ( Exception ):
    """Base class for RegisterException in this module."""
    pass

    
#///////////////////////////////////////////////   
    

@route( '/', method = "GET" )
def web_main( ):
    
    try:
        user = check_login()
        if ( user ):
            return "Welcome to the prefstore, user: %s" % ( user, )
        else:
            return "Welcome to the prefstore. Please login."
    
    except RegisterException, e:
        redirect( "/register" )
        
    except LoginException, e:
        return error( e.msg )
    
    except Exception, e:
        return error( e )
        

#///////////////////////////////////////////////


def valid_email( str ):
    return re.search( "^[A-Za-z0-9%._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$", str )


#///////////////////////////////////////////////


def valid_name( str ):
    return  re.search( "^[A-Za-z0-9 ']{3,64}$", str )


#///////////////////////////////////////////////


@route( '/register', method = "GET" )
def register():
    
    #TODO: first check the user is logged in!
    
    try:
        user_id = extract_user_id()
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e )
    
    errors = {}
    
    #if the user has submitted registration info, parse it
    try: 
        request.GET[ "submission" ]
        submission = True;
    except:
        submission = False
        
    if ( submission ): 
        #validate the screen name supplied by the user
        try:
            screen_name = request.GET[ "screen_name" ]
            if ( not valid_name( screen_name ) ):
                errors[ 'screen_name' ] = "Must be 3-64 legal characters"    
        except:
            errors[ 'screen_name' ] = "You must supply a valid screen name"
    
        #validate the email address supplied by the user
        try:
            email = request.GET[ "email" ]
            if ( not valid_email( email ) ):
                errors[ 'email' ] = "The supplied email address is invalid"
            else: 
                match = prefdb.fetch_user_by_email( email )
                if ( not match is None ):
                    errors[ 'email' ] = "That email has already been taken"
        except:
            errors[ 'email' ] = "You must supply a valid email"


        #if everything is okay so far, add the data to the database    
        if ( len( errors ) == 0 ):
            try:
                prefdb.insert_registration( user_id, screen_name, email)
                prefdb.commit()
            except Exception, e:
                return error( e )

            redirect( ROOT_PAGE )

    #if this is the first visit to the page, or there are errors 
    return  """
        <div id="registerBox" class="displayBox">
        <form action="%s/register" method="GET" >
            <div class="left">Screen Name</div>
            <div class="right" >
                <input id="jid" class="text" name="screen_name" type="text" />
            </div>
            <div class="left">Email</div>
            <div class="right">
                <input id="email" class="text" name="email" type="text" />
            </div>
            <div id="loginMessage" class="loginMessage"></div>
            <input type="hidden" name="submission" value="True" />
            <input type="submit" value="Register" />
                </div>
            </form>
        </div>
    """ % ( REALM, )


#///////////////////////////////////////////////


@route( '/error', method = "GET" )
def error( e ):
    return "error: %s" % ( e )

      
#///////////////////////////////////////////////  
    
    
def extract_user_id():
    
    cookie = request.get_cookie( EXTENSION_COOKIE )
        
    #is the user logged in? First check we have a cookie...
    if cookie:
        #and that it contains suitably formatted data
        try:
            data = json.loads( cookie )
        except:
            delete_authentication_cookie()
            raise LoginException( "Your login data is corrupted. Resetting." )
        
        #and then that it contains a valid user_id
        try:
            user_id =  data[ "user_id" ]
            return user_id
        except:
            delete_authentication_cookie()
            raise LoginException( "You are logged in but have no user_id. Resetting." )
    else:
        return None

  
#///////////////////////////////////////////////  
    
    
def check_login():

    #first try and extract the user_id from the cookie. 
    #n.b. this can generate LoginExceptions
    user_id = extract_user_id()
    
    if ( user_id ) :
        
        #we should have a record of this id, from when it was authenticated
        user = prefdb.fetch_user_by_id( user_id )
        if ( not user ):
            delete_authentication_cookie()
            raise LoginException( "We have no record of the id supplied. Resetting." )
        
        #and finally lets check to see if the user has registered their details
        if ( user[ "screen_name" ] is None ):
            raise RegisterException()
        
        return user
        
    #if the user has made it this far, their page can be processed accordingly
    else:
        return None   
    
 
    
#//////////////////////////////////////////////////////////
# PREFSTORE SPECIFIC CHROME-API CALLS
#//////////////////////////////////////////////////////////


schema = {
    "type" : "object",
        "properties" : {
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
            "fv" : {
                "type" : "object",
                "patternProperties": { ".*": { "type": "integer" } } 
            }      
        }
    }   

    
#///////////////////////////////////////////////


#TODO: this should be part of the (private) database api
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
        prefdb.reconnect()
        return func();
    
    
#///////////////////////////////////////////////


@route( '/submitDistill', method = "POST" )
def submitDistill():
    """ 
        A Distillation is packaged as a json message of the form
        {user:u, docid:d, docType:t, appName:a, duration:d, mtime:m, fv:{ word:freq } }    
    """

    try:
        # First extracted the necessary POST parameters
        user_id = request.forms.get( 'user_id' )
        data = request.forms.get( 'data' ) 
    except:
        logging.debug( 
            "%s: Incorrect parameters in submission API call" 
            % ( "prefstore", user_id ) 
        )
        return "{'success':false,'cause':'required parameters missing'}"
        

    try:
        #convert the data into a json object
        data = json.loads( data )
        
        #Make sure the message is in the correct distill format.
        validictory.validate( data, schema )
               
    except ValueError, e:
        logging.error( 
            "%s: JSON validation error - %s" 
            % ( "prefstore", e ) 
        )          
        return "{'success':false,'cause':'JSON error'}"       
        
    
    # Log that we have received the distill message.
    logging.debug( 
        "%s: Message from '%s' successfully unpacked" 
        % ( "prefstore", user_id ) 
    )
    
       
    try:    
        # First db interaction of this method so safety check in case 
        # a mysql timeout has occurred since we last accessed the db.
        user = safetyCall( lambda: prefdb.fetch_user_by_id( user_id ) )
    except Exception, e: 
        logging.error( 
            "%s: User Lookup Error for Message from '%s'" 
            % ( "prefstore", e ) 
        )          
        return "{'success':false,'cause':'User Lookup error'}"   
    
    
    # Authenticate the user, using the supplied key
    if user:
        
        logging.debug( 
            "%s: Message successfully authenticated as belonging to '%s'" 
            % ( "prefstore", user[ "screen_name" ]  ) 
        )

        # And finally process it into the database
        try:
            processDistill( user, data )
            return "{'success':true}"
        except:
            logging.info( 
                "%s: Processing Failure for message from '%s'" 
                % ( "prefstore", user )
            ) 
            return "{'success':false,'cause':'Processing error'}"
    
    else:
        logging.warning( 
            "%s: Identification Failure for message from '%s'" 
            % ( "prefstore", user_id ) 
        )
        return "{'success':false,'cause':'Authentication error'}"
            
    
#///////////////////////////////////////////////        
       
        
def processDistill( user, data ) :
    
    #Extract entry information
    user_id =  user[ "user_id" ]
    mtime = data.get( 'mtime' )
    fv = data.get( 'fv' )
    
    #Update user info, incrementing the number of documents we have received.
    userUpdated = prefdb.incrementUserInfo( user_id, mtime )
    
    if not userUpdated :
        logging.error( 
            "%s: User '%s' could not be updated. Ignoring." 
            % ( "prefstore", user[ "screen_name" ] ) 
        )
        return False    

    #Split the terms into ones that exist in the db, and ones that don't
    terms = prefdb.removeBlackListed( [ term for term in fv ] )
    existingDictTerms = prefdb.matchExistingTerms( terms )
    newTerms = [ term for term in terms if term not in existingDictTerms ]
    processedTerms = 0

    #Process the terms we haven't seen before
    for term in newTerms:
        try:
            prefdb.insertDictionaryTerm( term )
        except:
            logging.warning( 
                "%s: Failed to add term '%s' to dictionary"
                % ( "prefstore", term, user_id ) 
            )
 
    #Process the terms that already exist in the dictinoary            
    for term in terms:
        try:
            prefdb.updateTermAppearance( user_id, term, fv.get( term ) );    
            processedTerms += 1
        except:
            logging.warning( 
                "%s: Failed to increment term '%s' for '%s'" 
                % ( "prefstore", term, user_id ) 
            )
            
    #Everything seems okay, so commit the transaction
    prefdb.commit()
    
    #Log the distillation results
    logging.info( 
        "%s: Message from '%s' (%d terms, %d extant, %d new, %d processed)" 
        % ( "prefstore", user["screen_name"], len( terms ), len( existingDictTerms ), len( newTerms ), processedTerms ) 
    )
    
    #And return from the function successfully
    return True
        

#///////////////////////////////////////////////   


@route('/static/:filename')
def get_static_file(filename):
    return static_file(filename, root='static/')


#///////////////////////////////////////////////  

   
@route('/data')
def data():
    
    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" )
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e )        
        
    #if the user doesn't exist or is not logged in, send them home
    if ( not user ) :
        redirect( ROOT_PAGE )
    
    try:
        type = request.GET[ "type" ]
    except:
        type = None
        
        
    try:
        message = "top 500 terms by total appearances"
        match_type = ""
        search_term = ""
        order_by = ""
        direction = ""
        
        if ( type == "search" ):
            try:
                search_term = request.GET[ "search_term" ]
                match_type = request.GET[ "match_type" ] 
            except:
                pass
            results =  prefdb.search_terms( user[ "user_id" ], search_term, match_type )
            message = "'%s' search for '%s' - %d results" % ( match_type, search_term, len( results ) ) 
        
        elif ( type == "filter" ):
            try:
                direction = request.GET[ "direction" ]
                order_by = request.GET[ "order_by" ] 
            except:
                pass
            results =  prefdb.fetch_terms( user[ "user_id" ], order_by, direction  )
            message = "filtered on '%s' - %s %d results" % ( 
                order_by, 
                "bottom" if direction == "ASC" else "top", 
                len( results )
            ) 
        else:
            results =  prefdb.fetch_terms( user[ "user_id" ] )
            message = "top 500 results" 
        
        
        data = ""
        
        if results:
            for row in results:
                
                term = row[ 'term' ]
                appearances = row[ 'total_appearances' ]
                inDocuments = row[ 'doc_appearances' ]
                #TODO: calculate this. Its the relative term frequency
                relevence = 0.32
                #TODO: Divide this by the total web docs.
                prevalence = row[ 'count' ]
                
                #TODO: Add this field to the database, and fix all the bugs it causes!
                last_seen = 1315410841
                last_seen_str = time.strftime("%d %b %Y %H:%M", time.gmtime( last_seen ) )
                
                data += """
                    { c:[{v:'%s'},{v:%d,f:%s},{v:%d,f:%s},{v:%d,f:%s},{v:%d,f:%s},{v:%d,f:'%s'}]},
                """ % ( 
                    term, 
                    appearances, str( appearances ), 
                    inDocuments, str( inDocuments ),
                    prevalence, str( prevalence ),
                    relevence, str( relevence ),            
                    last_seen, last_seen_str
                )
        
        return template(
            'data_management_template',
             data=data,
             type=type,
             search_term=search_term,
             match_type=match_type,
             order_by=order_by, 
             direction=direction,
             message=message
        )
  
    except Exception, e:
        return error( e )        
  

           
#//////////////////////////////////////////////////////////
# MAIN FUNCTION
#//////////////////////////////////////////////////////////


if __name__ == '__main__' :
    
    #-------------------------------
    # setup logging
    #-------------------------------
    
    logging.basicConfig( 
        format= '%(asctime)s [%(levelname)s] %(message)s', 
        datefmt='%Y-%m-%d %I:%M:%S',
        #filename='logs/prefstore.log',
        level=logging.DEBUG 
    )

    #-------------------------------
    # constants
    #-------------------------------
    EXTENSION_COOKIE = "logged_in"
    PORT = 8080
    REALM = "http://localhost:8080"
    ROOT_PAGE = "/"
        
    #-------------------------------
    # initialization
    #-------------------------------
    try:    
        pm = ProcessingModule.ProcessingModule()
    except Exception, e:
        logging.error( "Processing Module failure: %s" % ( e, ) )
        exit()

    prefdb = PrefstoreDB.PrefstoreDB()  
    prefdb.connect()
    prefdb.check_tables()
    
    logging.info( "database initialisation completed... [SUCCESS]" );
        
    updater = WebCountUpdater()
    updater.start()
                
    logging.info( "web updater initialisation completed... [SUCCESS]" );
        
    try:
        debug( True )
        run( host='0.0.0.0', port=PORT )
    except Exception, e:
        logging.error( "Web Server Startup failed: %s" % ( e, ) )
        exit()
        

   
   
