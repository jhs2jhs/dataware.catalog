"""
Created on 12 April 2011
@author: jog
"""

from new import * #@UnusedWildImport
import json
import MySQLdb
import logging
import urllib
import urllib2
import base64
import hashlib
import random

#setup logger for this module
log = logging.getLogger( "console_log" )

#///////////////////////////////////////////////


class Status( object ):
    
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"  
   
#///////////////////////////////////////////////
    
    
class AuthorizationException ( Exception ):
    def __init__(self, msg):
        self.msg = msg
        

#///////////////////////////////////////////////  


class PermitException ( Exception ):
    def __init__(self, msg):
        self.msg = msg


#///////////////////////////////////////////////  


class RejectionException ( Exception ):
    def __init__(self, msg):
        self.msg = msg


#///////////////////////////////////////////////  


class RevocationException ( Exception ):
    def __init__(self, msg):
        self.msg = msg
        
                   
#///////////////////////////////////////////////  


class RevokeException ( Exception ):
    def __init__(self, msg):
        self.msg = msg
       
                   
#///////////////////////////////////////////////

 
class AuthorizationModule( object ) :

    _WEB_PROXY =  None
    db = None
    
    #///////////////////////////////////////////////
    
    
    def __init__( self, db = None, web_proxy = None ):
        
        if db:
            self.db = db 
        else:
            raise Exception( "Database object parameter is missing" )
        
        if not web_proxy is None:
            self._WEB_PROXY =  { 'http' : web_proxy }
        
       
    #///////////////////////////////////////////////
        
        
    def __del__(self):
        if self.db.connected: 
            self.db.close(); 
        
            
    #///////////////////////////////////////////////
    
    
    def _format_submission_success( self, result = None ):
        
        if ( result ) :
            json_response = { 'success' : True, 'return' : result }
        else : 
            json_response = { 'success' : True }

        return json.dumps( json_response );
    
        
    #///////////////////////////////////////////////


    def _format_submission_failure( self, error, error_description ):
        
        json_response = { 
            'success' : False,
            'error' : error,
            'error_description' : error_description,            
        } 
        
        return json.dumps( json_response );
                
        
    #///////////////////////////////////////////////
    
    
    def _format_access_success( self, access_token ):
        
        json_response = { 
            'success' : True, 
            'access_token': access_token,
        }
        
        return json.dumps( json_response );
    
     
    #///////////////////////////////////////////////


    def _format_access_failure( self, error, msg = None ):
        
        json_response = { 
            'success' : False,
            'error':error,
            'error_description':msg
        } 
        
        return json.dumps( json_response );
     
             
    #///////////////////////////////////////////////

        
    def _format_auth_success( self, 
        redirect_uri, state, auth_code, resource_access_uri = None ):

        url =  "%s?state=%s&code=%s" % \
            ( redirect_uri, state, auth_code ) 

        json_response = { 
            'success':True, 
            'redirect':url
        } 
            
        return json.dumps( json_response )


    #///////////////////////////////////////////////
    
    
    def _format_auth_failure( self, redirect_uri, state, error ):

        url = "%s?state=%s&error=access_denied&error_description=%s" % \
            ( redirect_uri, state, error ) 

        json_response = { 
            'success':False, 
            'error':error, 
            'cause':"resource_provider", 
            'redirect':url 
        } 
            
        return json.dumps( json_response )        
    
    
    #///////////////////////////////////////////////


    def _format_revoke_success( self, redirect_uri, state, error ):

        url = "%s?state=%s&error=access_denied&error_description=%s" % \
            ( redirect_uri, state, error ) 

        json_response = { 
            'success':True, 
            'redirect':url 
        } 
            
        return json.dumps( json_response )         
    
         
    #///////////////////////////////////////////////


    def _format_failure( self, error, cause = "catalog" ):
        
        json_response = { 
            'success':False, 
            'error':error, 
            'cause':cause
        } 
            
        return json.dumps( json_response )
             

    #///////////////////////////////////////////////
    
    
    def resource_register( self, resource_name, 
        resource_uri, description, logo_uri, web_uri, namespace ):
        
        #check we have all the required paramters 
        if resource_name is None :
            return self._format_submission_failure(
                "catalog_denied", "A valid resource_name must be provided" )
        
        if resource_name is None :
            return self._format_submission_failure(
                "catalog_denied", "A valid redirect_uri must be provided" )
        
        if resource_name is None :
            return self._format_submission_failure(
                "catalog_denied", "A valid dataware namespace must be provided" )
        
        #also confirm that its and endpoint (not a directory)
        if resource_uri[ -1 ] == "/":
            return self._format_submission_failure(
                "catalog_denied", 
                "your redirect URI must not end with /" )
        
        #check the resource does not clash with a previously registered one
        resource = self.db.resource_fetch_by_name( resource_name )

        if ( resource ) :        
            return self._format_submission_failure(
                "catalog_denied",                
                "A resource with that name already exists in the catalog" ) 

        try:
            resource_id = self._generate_access_code()
  
            self.db.resource_insert( 
                resource_id = resource_id,                                    
                resource_name = resource_name,
                resource_uri = resource_uri,
                description = description,
                logo_uri = logo_uri,
                web_uri = web_uri,
                namespace = namespace,
            )

            self.db.commit()

            json_response = { 
                'success': True,
                'resource_id': resource_id
            } 
        
            return json.dumps( json_response );                
            
         
        except:    
            return self._format_submission_failure(
                "catalog_problems",                
                "Database problems are currently being experienced at the catalog"
            ) 
            
            
    #///////////////////////////////////////////////
    
    
    def resource_authorize( self, user, resource_id, resource_uri, state ):
       
        try:   
            if not ( user ) :        
                return self._format_failure( 
                    "A valid user ID and has not been provided." )

            if not ( resource_id ) :
                return self._format_failure( 
                    "A valid resource ID and has not been provided." )   

            #check that the resource has been registered
            resource = self.db.resource_fetch_by_id( resource_id )
            if not ( resource ) :
                return self._format_failure( 
                    "The resource has not been registered, and so cannot be installed." ) 

            if not ( resource[ "resource_uri" ] == resource_uri ) :
                return self._format_failure( 
                    "Incorrect resource credentials have been supplied." ) 

            #check that the user hasn't already been installed the resource
            if( self.db.install_fetch_by_id( user[ "user_id" ], resource_id ) ):
                return self._format_failure( 
                    "You have already installed this resource." ) 

            #all is well so create some access_token and authorization codes
            #register the request as having been updated.
            install_token = self._generate_access_code()
            auth_code = self._generate_access_code()
            
            self.db.install_insert( 
                user[ "user_id" ],
                resource_id, 
                state,
                install_token,
                auth_code                
            )
            
            self.db.commit()
            
            #the request has been accepted so return a success redirect url
            return self._format_auth_success(
                 "%s/install_complete" % ( resource_uri, ),  
                 state, 
                 auth_code
            )                            

        except:
            return self._format_failure( 
                "Server is currently experiencing undetermined problems. \
                Please try again later." )   
            
    
    #///////////////////////////////////////////////
    
    
    def resource_access( self, grant_type, resource_uri, auth_code ):
        
        try:

            if grant_type != "authorization_code" :
                return self._format_access_failure(
                    "unsupported_grant_type",
                    "Grant type is either missing or incorrect"
                )  
                                
            if ( auth_code is None ) :
                return self._format_access_failure(
                    "invalid_request",
                    "A valid authorization code has not been provided"
                )  

            #so far so good. Fetch the request that corresponds 
            #to the auth_code that has been supplied
            try:
                resource = self.db.install_fetch_by_auth_code( auth_code )
                
                if resource == None :
                    return self._format_access_failure(
                        "invalid_grant", 
                        "Authorization Code supplied is unrecognized" 
                    )  
                
                if not resource[ "install_token" ]  :
                    return self._format_access_failure(
                        "server_error", 
                        "No access token seems to be available for that code" 
                    )
            
                return self._format_access_success( resource[ "install_token" ] ) 
            
            #determine if there has been a database error
            except MySQLdb.Error:
                return self._format_access_failure(
                    "server_error", 
                    "Database problems are currently being experienced" 
                ) 

        #determine if there has been a database error
        except Exception:
            return self._format_access_failure(
                "server_error", 
                "An unknown error has occurred" 
            )   
            

        

    #///////////////////////////////////////////////
       
    
    def client_register( self, client_name, client_uri,
        description, logo_uri, web_uri, namespace ):
       
        if ( client_name is None or client_uri is None ) :
            return self._format_submission_failure(
                "catalog_denied",  
                "A valid client_name and redirect_uri must be provided" )
        
        #also confirm that its and endpoint (not a directory)
        if client_uri[ -1 ] == "/":
            return self._format_submission_failure(
                "catalog_denied", 
                "your redirect URI must not end with /" )

        #check that the user_id exists and is valid
        client = self.db.client_fetch_by_name( client_name )
        if ( client ) :        
            return self._format_submission_failure(
                "catalog_denied",
                "A client with that name already exists in the catalog" ) 
        
        try:
            client_id = self._generate_access_code()
        
            self.db.client_insert( 
                client_id = client_id,                                    
                client_name = client_name,
                client_uri = client_uri,
                description = description,
                logo_uri = logo_uri,
                web_uri = web_uri,
                namespace = namespace,
            )
            
            self.db.commit()

            json_response = { 
                'success': True,
                'client_id': client_id
            } 
        
            return json.dumps( json_response );                
            
         
        except:    
            return self._format_submission_failure(
                "catalog_problems",                
                "Database problems are currently being experienced at the catalog"
            )
                 
    
    #///////////////////////////////////////////////
        
        
    def client_request( self, 
        user_name, client_id, state, client_uri, json_scope ):
        
        try:
            #check that the user_id exists and is valid
            user = self.db.user_fetch_by_name( user_name )
            if not ( user ) :        
                return self._format_submission_failure(
                    "invalid_request", "The specified user name is not recognized" ) 
     
            #check that the client_id exists and is valid
            client = self.db.client_fetch_by_id( client_id )
            if ( not client ) or client[ "client_uri" ] != client_uri  :        
                return self._format_submission_failure(
                    "unauthorized_client", "A valid client ID/redirect_uri pair has not been provided"
                ) 

            #check that the scope unpacks
            try:
                scope = json.loads( 
                    json_scope.replace( '\r\n','\n' ), 
                    strict=False 
                )
    
                resource_name = scope[ "resource_name" ]
                expiry_time = scope[ "expiry_time" ]
                query = scope[ "query" ] 
                
            except Exception, e:
                return self._format_submission_failure(
                    "invalid_scope", "incorrectly formatted JSON scope" ) 
            
            #check that the resource is installed by the user
            resource = self.db.install_fetch_by_name( 
                user[ "user_id" ],
                resource_name )

            if not resource:
                return self._format_submission_failure(
                    "invalid_request", "User does not have a resource installed by that name"
                )

            #so far so good. Add the request to the user's database
            #Note that if the resource the client has requested access to
            #doesn't exist, the database will throw a foreign key error.

            self.db.processor_insert( 
                user[ "user_id" ],                                    
                client_id, 
                state,
                resource[ "resource_id" ],
                expiry_time, 
                query,
                Status.PENDING
            )

            return self._format_submission_success() 
        
        #determine if there has been an integrity error
        except MySQLdb.IntegrityError, e:
            
            #primary key error - means the entry already exists
            if ( e[ 0 ] == 1062 ):
                return self._format_submission_failure(
                    "invalid_scope","Supplied Processor code is a duplicate"
                ) 
                
            #foreign key error (means that the specified resource is unknown)
            elif ( e[ 0 ] == 1452): 
                return self._format_submission_failure(
                    "invalid_request", "Problem tying resource name to supplied user"
                )
        
        #otherwise we have wider database problems
        except:   
            return self._format_submission_failure(
                "server_error", "Database problems are currently being experienced"
            ) 
            
    
    #///////////////////////////////////////////////
    
    
    def client_authorize( self, user_id, processor_id ):
        
        try:
            #check that the user_id exists and is valid
            user = self.db.user_fetch_by_id( user_id )
                    
            if not ( user ) :        
                return self._format_failure( 
                    "A valid user ID and has not been provided." )
                
            if not ( processor_id ) :
                return self._format_failure( 
                    "A valid processor ID and has not been provided." )   
                
            #check that the processor_id exists and is pending
            processor = self.db.processor_fetch_by_id( processor_id )

            if not ( processor ) :
                return self._format_failure( 
                    "The processing request you are trying to authorize does not exist." ) 
            
            if not ( processor[ "user_id" ] == user_id ) :
                return self._format_failure( 
                    "Incorrect user authentication for that processing request." ) 
            
            if ( not processor[ "request_status" ] == Status.PENDING ):
                return self._format_failure( 
                    "This request has already been authorized." )   

        
            #get the details about the resource and the targeted user state
            install = self.db.install_fetch_by_id( 
                user_id, 
                processor[ "resource_id" ] 
            )
            
            if not ( install ) :
                return self._format_failure( 
                    "You do not have the targeted resource installed" ) 
           
        
            #contact the resource provider and fetch the access token  
            try:    
                access_token = self._client_permit_request( processor, install )
                
            except PermitException, e:
                #the processing request has been rejected by the resource_provider
                #so we have to return a failure redirect url and mop up
                result = self.db.processor_delete( processor_id )
                self.db.commit()
                
                return self._format_auth_failure(
                    processor[ "redirect_uri" ],
                    processor[ "state" ],
                    e.msg )
            except:
                return self._format_failure(
                    "Authorization failed - unknown issue coordinating with \
                     Resource Provider. Try again later." )
        
            #all is well so register the processing request as having been updated.
            auth_code = self._generate_access_code()
            
            result = self.db.processor_update( 
                processor_id, 
                Status.ACCEPTED, 
                access_token,
                auth_code
            )

            if ( not result ):
                return self._format_failure( 
                    "Server is currently experiencing database problems. \
                     Please try again later." )     
                 
            self.db.commit()
            
            #the processing request has been accepted so return a success redirect url
            return self._format_auth_success(
                 processor[ "client_uri" ],  
                 processor[ "state" ], 
                 auth_code,
                 processor[ "resource_uri" ],
            )                            

        except:
            return self._format_failure( 
                "Server is currently experiencing undetermined problems. \
                Please try again later." )     
    
               
    #///////////////////////////////////////////////
    
      
    def _client_permit_request( self, processor, install ):
        """
            Once the user has accepted an authorization request, the catalog
            must check that the resource provider is happy to permit the query 
            to be run on its server. If this fails a RegisterException will
            be thrown that the calling function must handle accordingly.
        """
        
        #build up the required data parameters for the communication
        data = urllib.urlencode( {
                'install_token': install[ "install_token" ],
                'client_id': processor[ "client_id" ],
                'query': processor[ "query" ],
                'expiry_time': processor[ "expiry_time" ],
            }
        )
                        
        url = "%s/permit_processor" % ( processor[ "resource_uri" ], )

        #if necessary setup a proxy
        if ( self._WEB_PROXY ):
            proxy = urllib2.ProxyHandler( self._WEB_PROXY )
            opener = urllib2.build_opener( proxy )
            urllib2.install_opener( opener )

        #first communicate with the resource provider   
        try:
            req = urllib2.Request( url, data )
            response = urllib2.urlopen( req )
            output = response.read()
        except urllib2.URLError, e:
            raise PermitException( "Failure - could not contact resource provider (%s)" % e )
        
        #parse the json response from the provider
        try:
            output = json.loads( 
                output.replace( '\r\n','\n' ), 
                strict=False 
            )

        except:
            raise PermitException( "Invalid json returned by the resource provider" )
        
        #determine whether the processor has been successfully
        #permitted by the resource provider
        try:
            success = output[ "success" ]
        except:
            #if we don't get a response then the agreed schema has
            #not been fulfilled by the resource provider. Bail.
            raise PermitException( "Resource provider has not returned successfully - unknown error" )

        #if it has then extract the access_token that will be used
        if success:
            try:
                return output[ "access_token" ]
            except:
                #something has gone seriously wrong with the resource provider's
                #handling of the communication as it should have returned a key
                cause = "Resource provider failed to supply access token" 
        else: 
            try:
                #if there is a problem we should have been sent a cause
                cause = "%s: %s" % ( output[ "error" ], output[ "error_description" ], )
            except:
                #if not simply report that we don't know what has gone awry
                cause = "Unknown problems accepting processor."
        
        #if we have reached here something has gone wrong - report it        
        raise PermitException( cause )
    
    
    #///////////////////////////////////////////////
    
    
    def client_access( self, grant_type, client_uri, auth_code ):
         
        try:

            if grant_type != "authorization_code" :
                return self._format_access_failure(
                    "unsupported_grant_type",
                    "Grant type is either missing or incorrect"
                )  
                                
            if ( auth_code is None ) :
                return self._format_access_failure(
                    "invalid_request",
                    "A valid authorization code has not been provided"
                )  

            #so far so good. Fetch the request that corresponds 
            #to the auth_code that has been supplied
            try:
                processor = self.db.processor_fetch_by_auth_code( auth_code )
                
                if processor == None :
                    return self._format_access_failure(
                        "invalid_grant", 
                        "Authorization Code supplied is unrecognized" 
                    )  
                
                if not processor[ "access_token" ]  :
                    return self._format_access_failure(
                        "server_error", 
                        "No access token seems to be available for that code" 
                    )
            
                return self._format_access_success( processor[ "access_token" ] ) 
            
            #determine if there has been a database error
            except MySQLdb.Error:
                return self._format_access_failure(
                    "server_error", 
                    "Database problems are currently being experienced" 
                ) 

        #determine if there has been a database error
        except Exception:
            return self._format_access_failure(
                "server_error", 
                "An unknown error has occurred" 
            )        

 
    #///////////////////////////////////////////////
     
    
    def client_reject( self, user_id, processor_id ):

        try:   
            #check that the user_id exists and is valid
            user = self.db.user_fetch_by_id( user_id )

            if not ( user ) :
                return self._format_failure( 
                    "A valid user ID and has not been provided." )
            
            if not ( processor_id ) :        
                return self._format_failure( 
                    "A valid processor ID and has not been provided." )
 
            #check that the processor_id exists and is pending
            processor = self.db.processor_fetch_by_id( processor_id )

            if not ( processor ) :
                return self._format_failure( 
                    "The processing request you are trying to reject does not exist." ) 
            
            if not ( processor[ "user_id" ] == user_id ) :
                return self._format_failure( 
                    "Incorrect user authentication for that request." ) 
            
            if ( not processor[ "request_status" ] == Status.PENDING ):
                return self._format_failure( 
                    "This processing request has already been authorized." )   

            result = self.db.processor_delete( processor_id )

            if ( not result ):
                return self._format_failure( 
                    "Server is currently experiencing database problems. Please try again later." )     

            self.db.commit()

            #the processor has been revoked so build the redirect url that
            #will notify the client via the user's browser
            return self._format_revoke_success( 
                processor[ "client_uri" ],
                processor[ "state" ],
                "The user denied your processing request."
            )

        except:
            return self._format_failure( 
                "Server is currently experiencing undetermined problems. Please try again later." )            
                
    
    #///////////////////////////////////////////////
    
    
    def client_revoke( self, user_id, processor_id ):
        
        try:   
            #check that the user_id exists and is valid
            user = self.db.user_fetch_by_id( user_id )

            if not ( user ) :        
                return self._format_failure( 
                    "A valid user ID and has not been provided." )
                
            if not ( processor_id ) :
                return self._format_failure( 
                    "A valid processor ID and has not been provided." )        
                    
            #check that the processor_id exists and is pending
            access_request = self.db.processor_fetch_by_id( processor_id )

            if not ( access_request ) :        
                return self._format_failure( 
                    "The processing request that you are trying to revoke does not exist." ) 
            
            if not ( access_request[ "user_id" ] == user_id ) :        
                return self._format_failure( 
                    "Incorrect user authentication for that processing request." ) 
                         
            if ( not access_request[ "request_status" ] == Status.ACCEPTED ):
                return self._format_failure( 
                    "This processing request has not been authorized, and so cannot be revoked." )   

            # contact the resource provider and tell them we have cancelled the
            # request so they should delete it, and its access_token from their records
            try:     
                self._client_revoke_request( access_request )
                
            except RevokeException, e:
                return self._format_failure(
                    "Abandoned revoke - problem at Resource Provider: \"%s\"." % ( e.msg, ),
                    "resource_provider" )      
            except:
                return self._format_failure( 
                    "Abandoned revoke - undetermined problem at Resource Provider", 
                    "resource_provider" )

            result = self.db.processor_delete( processor_id )
            
            if ( not result ):
                return self._format_failure( 
                    "Server is currently experiencing database problems. Please try again later." )     

            self.db.commit()

            return self._format_revoke_success( 
                access_request[ "client_uri" ],
                access_request[ "state" ],
                "The user revoked your processor request."
            )

        except:

            return self._format_failure( 
                "Server is currently experiencing problems. \
                Please try again later." )            
        

    #///////////////////////////////////////////////
    
    
    def _client_revoke_request( self, processor ):
        
        """
            Once the user has revoked an authorization request, the catalog
            must tell the resource provider to deregister that query 
        """
        
        #build up the required data parameters for the communication
        data = urllib.urlencode( {
                'install_token': processor[ "install_token" ],
                'access_token': processor[ "access_token" ],
            }
        )
        
        url = "%s/revoke_processor" % ( processor[ "resource_uri" ], )
        
        #if necessary setup a proxy
        if ( self._WEB_PROXY ):
            proxy = urllib2.ProxyHandler( self._WEB_PROXY )
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
         
        #first communicate with the resource provider   
        try:
            req = urllib2.Request( url, data )
            response = urllib2.urlopen( req )
            output = response.read()
        except urllib2.URLError:
            raise RevokeException( "Resource provider uncontactable. Please Try again later." )

        #parse the json response from the provider
        try:
            output = json.loads( 
                output.replace( '\r\n','\n' ), 
                strict=False 
            )

        except:
            raise RevokeException( "Invalid json returned by the resource provider" )

        #determine whether the processor has been successfully
        #revoked by the resource provider
        try:
            success = output[ "success" ]
        except:
            #if we don't get a response then the agreed schema has
            #not been fulfilled by the resource provider. Bail.
            raise RevokeException( "Resource provider has not returned successfully - unknown error" )

        #if it has then extract the access_token that will be used
        if not success:
            try:
                #if there is a problem we should have been sent a cause
                cause = output[ "error" ][ "message" ]
            except:
                #if not simply report that we don't know what has gone awry
                cause = "reason unknown"
            
            raise RevokeException( cause )
        
    
    #///////////////////////////////////////////////
        
             
    def _generate_access_code( self ):
        
        token = base64.b64encode(  
            hashlib.sha256( 
                str( random.getrandbits( 256 ) ) 
            ).digest() 
        )  
            
        #replace plus signs with asterisks. Plus signs are reserved
        #characters in ajax transmissions, so just cause problems
        return token.replace( '+', '*' ) 

