"""
Created on 12 April 2011
@author: jog
"""

from __future__ import division
from bottle import * #@UnusedWildImport
import json
import logging
import urllib

import OpenIDManager
import AuthorizationModule
from CatalogDB import *  #@UnusedWildImport

#//////////////////////////////////////////////////////////
# CONSTANTS
#//////////////////////////////////////////////////////////

log = logging.getLogger( "console_log" )

class std_writer( object ):
    
    def __init__( self, msg ):
        self.msg = msg
        
    def write(self, data):
        data = data.replace( '\n', '' ) \
                   .replace( '\t', '' )
        if len( data ) > 0 :
            log.info( self.msg + ": " + data )


#//////////////////////////////////////////////////////////
# OPENID SPECIFIC WEB-API CALLS
#//////////////////////////////////////////////////////////


@route( '/login', method = "GET" )
def openID_login():

    try:
        params = "resource_id=%s&redirect_uri=%s&state=%s" % \
            ( request.GET[ "resource_id" ],
              request.GET[ "redirect_uri" ], 
              request.GET[ "state" ], )
    except:
        params = ""
    
    print params
    
    try: 
        username = request.GET[ 'username' ]    
    except: 
        username = None
     
    try:      
        provider = request.GET[ 'provider' ]
    except: 
        return template( 
            'login_page_template', 
            REALM=REALM, user=None, params=params )    
    try:
        url = OpenIDManager.process(
            realm=REALM,
            return_to=REALM + "/checkauth?" + urllib.quote( params ),
            provider=provider,
            username=username
        )
    except Exception, e:
        return error( e )
    
    print url
    #Here we do a javascript redirect. A 302 redirect won't work
    #if the calling page is within a frame (due to the requirements
    #of some openid providers who forbid frame embedding), and the 
    #template engine does some odd url encoding that causes problems.
    return "<script>self.parent.location = '%s'</script>" % (url,)
    

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
                user = db.fetch_user_by_id( user_id )
                
                #if this is a new user add them
                if ( not user ):
                    db.insert_user( o.get_user_id() )
                    db.commit()
                    user_name = None
                else :
                    user_name = user[ "user_name" ]
                
                set_authentication_cookie( user_id, user_name  )
                
            except Exception, e:
                return error( e )
            
            
        #if they don't something has gone horribly wrong, so mop up
        else:
            delete_authentication_cookie()

    #else make sure the user is still logged out
    else:
        delete_authentication_cookie()
        
    try:
        redirect_uri = "resource_request?resource_id=%s&redirect_uri=%s&state=%s" % \
            ( request.GET[ "resource_id" ], 
              request.GET[ "redirect_uri" ], 
              request.GET[ "state" ] )
    except:
        redirect_uri = REALM + ROOT_PAGE
    
    print redirect_uri
    return "<script>self.parent.location = '%s'</script>" % ( redirect_uri, )
       
                
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
            
            
#///////////////////////////////////////////////


def set_authentication_cookie( user_id, user_name = None ):
    
    #if the user has no "user_name" it means that they
    #haven't registered an account yet    
    if ( not user_name ):
        json = '{"user_id":"%s","user_name":null}' \
            % ( user_id, )
        
    else:
        json = '{"user_id":"%s","user_name":"%s"}' \
            % ( user_id, user_name )
         
    response.set_cookie( EXTENSION_COOKIE, json )
    

#//////////////////////////////////////////////////////////
# CATALOG SPECIFIC WEB-API CALLS
#//////////////////////////////////////////////////////////

   
#TODO: make sure that redirect uri's don't have a / on the end
@route( '/resource_register', method = "POST" )
def resource_register():
    
    resource_name = request.forms.get( 'resource_name' )   
    redirect_uri = request.forms.get( 'redirect_uri' )
    description = request.forms.get( 'description' )
    logo_uri = request.forms.get( 'logo_uri' )
    web_uri = request.forms.get( 'web_uri' )
    namespace = request.forms.get( 'namespace' )
        
    result = am.resource_register( 
        resource_name = resource_name,
        redirect_uri = redirect_uri,
        description = description,
        logo_uri = logo_uri,
        web_uri = web_uri,
        namespace = namespace,
    )
    
    log.debug( 
        "Catalog_server: Resource Registration for client '%s': %s" 
        % ( resource_name, result ) 
    )
        
    return result    
    
    
#//////////////////////////////////////////////////////////

    
@route( '/resource_request', method = "GET" )
def resource_request( user_name = None ):

    #first check that required parameters have beeing supplied
    try: 
        resource_id = request.GET[ "resource_id" ]
        redirect_uri = request.GET[ "redirect_uri" ]
        state = request.GET[ "state" ]
    except:
        return template( 'resource_request_error_template', 
           error = "The resource has not supplied the right parameters." 
        );

    #Then check that the resource has registered
    resource = db.fetch_resource_by_id( resource_id ) 
    if ( not resource ):
        return template( 'resource_request_error_template', 
           error = "Resource isn't registered with us, so cannot install."
        );
    
    #And finally check that it has supplied the correct credentials
    if ( resource[ "redirect_uri" ] != redirect_uri ):
        return template( 'resource_request_error_template', 
           error = "The resource has supplied incorrect credentials."
        );

    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" ) 
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e ) 

    return template( 'resource_request_template', 
        user=user,
        state=state,
        resource=resource
    );


#//////////////////////////////////////////////////////////
 

@route( '/resource_authorize', method = "POST" )
def resource_authorize():
    
    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" ) 
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e ) 
    
    resource_id = request.forms.get( 'resource_id' )   
    redirect_uri = request.forms.get( 'redirect_uri' )
    state = request.forms.get( 'state' )  

    result = am.resource_authorize( 
        user,
        resource_id = resource_id,
        redirect_uri = redirect_uri,
        state = state,
    )

    log.debug( 
        "Catalog_server: Resource Authorization Request from %s for %s completed" 
        % ( user[ "user_id" ], resource_id ) 
    )

    return result


#//////////////////////////////////////////////////////////


@route( '/client_register', method = "POST" )
def client_register():
    
    client_name = request.forms.get( 'client_name' )   
    redirect_uri = request.forms.get( 'redirect_uri' )
    description = request.forms.get( 'description' )
    logo_uri = request.forms.get( 'logo_uri' )
    web_uri = request.forms.get( 'web_uri' )
    namespace = request.forms.get( 'namespace' )
        
    result = am.client_register( 
        client_name = client_name,
        redirect_uri = redirect_uri,
        description = description,
        logo_uri = logo_uri,
        web_uri = web_uri,
        namespace = namespace,
    )
    
    log.debug( 
        "Catalog_server: Client Registration for client '%s': %s" 
        % ( client_name, result ) 
    )
        
    return result    
    
    
#//////////////////////////////////////////////////////////

    
@route( '/user/:user_name/client_request', method = "POST" )
def client_request( user_name = None ):

    client_id = request.forms.get( 'client_id' )
    state = request.forms.get( 'state' )
    redirect_uri = request.forms.get( 'redirect_uri' )
    json_scope = request.forms.get( 'scope' )
    
    result = am.client_request( 
        user_name = user_name,
        client_id = client_id,
        state = state,
        redirect_uri = redirect_uri,
        json_scope = json_scope 
    )
    
    log.debug( 
        "Catalog_server: Client Request from %s to %s: %s" 
        % ( client_id, user_name, result ) 
    )
        
    return result

    
#//////////////////////////////////////////////////////////
 

@route( '/client_client', method = "POST" )
def client_authorize():
    
    #by this point the user has authenticated and will have
    #a cookie identifying themselves. This is used to extract
    #their id. This will be an openid (working as an access key),
    #even though they have a publically exposed username. This
    #api call involves interaction via the user's web agent so
    #will redirect the user to the client if the access request
    #acceptance is successful, or display an appropriate error page
    #otherwise (e.g. if the resource provider rejects the request.

    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" ) 
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e ) 
    
    request_id = request.forms.get( 'request_id' )

    url = am.client_authorize( 
        user_id = user[ "user_id" ],
        request_id = request_id,
    )

    log.debug( 
        "Catalog_server: Authorization Request from %s for request %s completed" 
        % ( user[ "user_id"], request_id ) 
    )

    return url

    
    
#//////////////////////////////////////////////////////////
      
  
@route( '/access', method = "POST" )
def access():

    grant_type = request.forms.get( 'grant_type' )
    redirect_uri = request.forms.get( 'redirect_uri' )
    auth_code = request.forms.get( 'code' )
        
    result = am.access( 
        grant_type = grant_type,
        redirect_uri = redirect_uri,
        auth_code = auth_code 
    )
    
    return result


#//////////////////////////////////////////////////////////   
      

@route( '/reject_client', method = "POST" )
def reject_client():
    
    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" ) 
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e ) 
    
    request_id = request.forms.get( 'request_id' )

    result = am.reject_request( 
        user_id = user["user_id"],
        request_id = request_id,
    )

    log.debug( 
        "Catalog_server: Request rejection from %s for request %s" 
        % ( user["user_id"], request_id ) 
    )

    return result

    
#//////////////////////////////////////////////////////////   


@route( '/revoke_request', method = "POST" )
def revoke_request():
    
    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" ) 
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e ) 
    
    request_id = request.forms.get( 'request_id' )


    result = am.revoke_request( 
        user_id = user["user_id"],
        request_id = request_id,
    )

    log.debug( 
        "Catalog_server: Request %s has been successfully revoked by %s" \
         % ( request_id, user["user_id"] ) 
    )
    
    return result
                            

#//////////////////////////////////////////////////////////
# CATALOG SPECIFIC WEB-API CALLS
#//////////////////////////////////////////////////////////


class LoginException ( Exception ):
    def __init__(self, msg):
        self.msg = msg


#///////////////////////////////////////////////  


class RegisterException ( Exception ):
    """Base class for RegisterException in this module."""
    pass

    
#///////////////////////////////////////////////


def valid_email( str ):
    return re.search( "^[A-Za-z0-9%._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$", str )


#///////////////////////////////////////////////


def valid_name( str ):
    return re.search( "^[A-Za-z0-9 ']{3,64}$", str )


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
        #validate the user_name supplied by the user
        try:
            user_name = request.GET[ "user_name" ]
            if ( not valid_name( user_name ) ):
                errors[ 'user_name' ] = "Must be 3-64 legal characters"
            else: 
                match = db.fetch_user_by_name( user_name ) 
                if ( not match is None ):
                    errors[ 'user_name' ] = "That name has already been taken"                    
        except:
            errors[ 'user_name' ] = "You must supply a valid user name"
    
        #validate the email address supplied by the user
        try:
            email = request.GET[ "email" ]

            if ( not valid_email( email ) ):
                errors[ 'email' ] = "The supplied email address is invalid"
            else: 
                match = db.fetch_user_by_email( email ) 
                if ( not match is None ):
                    errors[ 'email' ] = "That email has already been taken"
        except:
            errors[ 'email' ] = "You must supply a valid email"


        #if everything is okay so far, add the data to the database    
        if ( len( errors ) == 0 ):
            try:
                match = db.insert_registration( user_id, user_name, email) 
                db.commit()
            except Exception, e:
                return error( e )

            #update the cookie with the new details
            set_authentication_cookie( user_id, user_name )
            
            #return the user to the home page
            redirect( ROOT_PAGE )
    
    else:
        email = ""
        user_name = ""
        
    #if this is the first visit to the page, or there are errors

    return template( 
        'register_page_template',
        REALM=REALM,  
        user=None, 
        email=email,
        user_name=user_name,
        errors=errors ) 
    

#///////////////////////////////////////////////


@route( '/error', method = "GET" )
def error( e ):
    return  "An error has occurred: %s" % ( e )

      
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
        user = db.fetch_user_by_id( user_id )
        
        if ( not user ):
            delete_authentication_cookie()
            raise LoginException( "We have no record of the id supplied. Resetting." )
        
        #and finally lets check to see if the user has registered their details
        if ( user[ "user_name" ] is None ):
            raise RegisterException()
        
        return user
        
    #if the user has made it this far, their page can be processed accordingly
    else:
        return None   
    
#///////////////////////////////////////////////  
    
@route('/static/:filename')
def get_static_file( filename ):
    return static_file( filename, root='static/' )


#///////////////////////////////////////////////  


@route( '/', method = "GET" )     
@route( '/home', method = "GET" )
def home( ):

    try:
        user = check_login()
    except RegisterException, e:
        redirect( "/register" ) 
    except LoginException, e:
        return error( e.msg )
    except Exception, e:
        return error( e )  
    
    return template( 'home_page_template', REALM=REALM, user=user );
       
 
    
#//////////////////////////////////////////////////////////
      
      
if __name__ == '__main__' :

    #-------------------------------
    # setup logging
    #-------------------------------
    log = logging.getLogger( 'console_log' )
    
    # set logging levels
    log.setLevel( logging.DEBUG )
   
    # create handlers
    ch = logging.StreamHandler( sys.stdout )
        
    # create formatter and add it to the handlers
    formatter = logging.Formatter( '--- %(asctime)s [%(levelname)s] %(message)s' )
    ch.setFormatter( formatter )
    
    # add the handlers to the logger
    log.addHandler( ch )

    # redirect standard outputs
    sys.stdout = std_writer( "stdout" )
    sys.stderr = std_writer( "stderr" )
       
    #-------------------------------
    # constants
    #-------------------------------
    EXTENSION_COOKIE = "catalog_logged_in"
    PORT = 8080
    REALM = "http://www.prefstore.org:8080" 
    ROOT_PAGE = "/"
    #LOCAL! REALM = "http://localhost:8080"
    #LOCAL! WEB_PROXY = "http://mainproxy.nottingham.ac.uk:8080"

    #-------------------------------
    # initialization
    #-------------------------------
    try:
        db = CatalogDB()
        db.connect()
        db.check_tables()
    except Exception, e:
        log.error( "Database Initialization failure: %s" % ( e, ) )
        exit()
        
    try:    
        am = AuthorizationModule.AuthorizationModule( db )
    except Exception, e:
        log.error( "Authorization Module failure: %s" % ( e, ) )
        exit()
    
    try:
        debug( True )
        run( host='0.0.0.0', port=PORT, quiet=False )
    except Exception, e:
        log.error( "Web Server Exception: %s" % ( e, ) )
        exit()
   
