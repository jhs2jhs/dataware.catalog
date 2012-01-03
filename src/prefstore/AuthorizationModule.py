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


class RegistrationException ( Exception ):
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


class DeregisterException ( Exception ):
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
    
    def format_submission_success( self, result = None ):
        
        if ( result ) :
            json_response = { 'success' : True, 'return' : result }
        else : 
            json_response = { 'success' : True }

        return json.dumps( json_response );
    
        
    #///////////////////////////////////////////////


    def format_submission_failure( self, error, error_description ):
        
        json_response = { 
            'success' : False,
            'error' : error,
            'error_description' : error_description,            
        } 
        
        return json.dumps( json_response );
                
        
    #///////////////////////////////////////////////
    
    
    def format_access_success( self, access_token ):
        
        json_response = { 'access_token': access_token,}
        return json.dumps( json_response );
    
     
    #///////////////////////////////////////////////


    def format_access_failure( self, error, msg = None ):
        
        json_response = { 
            'error':error,
            'error_description':msg
        } 
        
        return json.dumps( json_response );
     
             
    #///////////////////////////////////////////////

        
    def format_auth_success( self, redirect_uri, state, auth_code ):
        url =  "%s?state=%s&code=%s" % \
            ( redirect_uri, state, auth_code ) 
        return json.dumps( { 'success':True, 'redirect':url } )


    #///////////////////////////////////////////////
    
    
    def format_auth_failure( self, redirect_uri, state, error ):
        url = "%s?state=%s&error=access_denied&error_description=%s" % \
            ( redirect_uri, state, error ) 
        return json.dumps( 
            { 
                'success':False, 
                'error':error, 
                'cause':"resource_provider", 
                'redirect':url 
            } 
        )
    
    
    #///////////////////////////////////////////////


    def format_revoke_success( self, redirect_uri, state, error ):
        url = "%s?state=%s&error=access_denied&error_description=%s" % \
            ( redirect_uri, state, error ) 
        return json.dumps( { 'success':True, 'redirect':url } )
    
         
    #///////////////////////////////////////////////


    def format_failure( self, error, cause = "catalog" ):
        return json.dumps( { 'success':False, 'error':error, 'cause':cause } );
                 
                 
    #///////////////////////////////////////////////
    
    
    def client_registration( self, client_name, redirect_uri,
        description, logo_uri, web_uri, namespace ):
       
        if ( client_name is None or redirect_uri is None ) :
            return self.format_submission_failure(
                "registration_denied", "catalog_denied",
                "A valid client_name redirect_uri must be provided"
            )
        
        #check that the user_id exists and is valid
        client = self.db.fetch_client_by_name( client_name )
        if ( client ) :        
            return self.format_submission_failure(
                "registration_denied", "catalog_denied",                
                "A client with that name already exists in the catalog"
            ) 
        
        try:
            client_id = self.generateAuthorizationCode()
        
            self.db.insert_client_registration( 
                client_id = client_id,                                    
                client_name = client_name,
                redirect_uri = redirect_uri,
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
            return self.format_submission_failure(
                "registration_denied", "catalog_problems",                
                "Database problems are currently being experienced at the catalog"
            ) 
        
    
    #///////////////////////////////////////////////
        
        
    def processing_request( self, 
        user_name, client_id, state, 
        redirect_uri, json_scope ):
        
        try:
            #check that the user_id exists and is valid
            user = self.db.fetch_user_by_name( user_name )
            if not ( user ) :        
                return self.format_submission_failure(
                    "invalid_request", "A valid user ID has not been provided" ) 
               
            #check that the client_id exists and is valid
            client = self.db.fetch_client_by_id( client_id )
            if (not client) or client[ "redirect_uri" ] != redirect_uri  :        
                return self.format_submission_failure(
                    "unauthorized_client", "A valid client ID/redirect_uri pair has not been provided"
                ) 
    
                
            #check that the scope unpacks
            try:
                scope = json.loads( 
                    json_scope.replace( '\r\n','\n' ), 
                    strict=False 
                )
    
                resource_id = scope[ "resource_id" ]
                expiry_time = scope[ "expiry_time" ]
                query = scope[ "query" ] 
                
            except Exception, e:
                return self.format_submission_failure(
                    "invalid_scope", "incorrectly formatted JSON scope" ) 
            
            #so far so good. Add the request to the user's database
            #Note that if the resource the client has requested access to
            #doesn't exist, the database will throw a foreign key error.

            self.db.insert_access_request( 
                user[ "user_id" ],                                    
                client_id, 
                state,
                redirect_uri,
                resource_id,
                expiry_time, 
                query,
                Status.PENDING
            )
                
            return self.format_submission_success() 
        
        #determine if there has been an integrity error
        except MySQLdb.IntegrityError, e:
            
            #primary key error - means the entry already exists
            if ( e[ 0 ] == 1062 ):
                return self.format_submission_failure(
                    "invalid_scope","Supplied Processor code is a duplicate"
                ) 
                
            #foreign key error (means that the specified resource is unknown)
            elif ( e[ 0 ] == 1452): 
                return self.format_submission_failure(
                    "invalid_request", "A valid resource name has not been provided"
                )
        
        #otherwise we have wider database problems
        except:   
            return self.format_submission_failure(
                "server_error", "Database problems are currently being experienced"
            ) 
    
      
                
    #///////////////////////////////////////////////
    
    
    def authorize_request( self, user_id, request_id ):
        
        try:
            #check that the user_id exists and is valid
            user = self.db.fetch_user_by_id( user_id )
                    
            if not ( user ) :        
                return self.format_failure( 
                    "A valid user ID and has not been provided." )
                
            if not ( request_id ) :
                return self.format_failure( 
                    "A valid request ID and has not been provided." )   
                
            #check that the request_id exists and is pending
            access_request = self.db.fetch_request_by_id( request_id )

            if not ( access_request ) :
                return self.format_failure( 
                    "The request you are trying to reject does not exist." ) 
            
            if not ( access_request[ "user_id" ] == user_id ) :
                return self.format_failure( 
                    "Incorrect user authentication for that request." ) 
            
            if ( not access_request[ "request_status" ] == Status.PENDING ):
                return self.format_failure( 
                    "This request has already been authorized." )   

            #contact the resource provider and fetch the access token  
            try:    
                access_token = self.register_request( access_request )
            except RegistrationException, e:
                #the request has been rejected by the resource_provider
                #so we have to return a failure redirect url and mop up
                result = self.db.delete_request( request_id )
                self.db.commit()
                
                return self.format_auth_failure(
                    access_request[ "redirect_uri" ],
                    access_request[ "state" ],
                    e.msg )
            except:
                return self.format_failure(
                    "Authorization failed - unknown issue coordinating with \
                     Resource Provider. Try again later." )
        
            #all is well so register the request as having been updated.
            auth_code = self.generateAuthorizationCode()
            
            result = self.db.update_request( 
                request_id, 
                Status.ACCEPTED, 
                access_token,
                auth_code
            )

            if ( not result ):
                return self.format_failure( 
                    "Server is currently experiencing database problems. \
                     Please try again later." )     
                 
            self.db.commit()
            
            #the request has been accepted so return a success redirect url
            return self.format_auth_success(
                 access_request[ "redirect_uri" ],  
                 access_request[ "state" ], 
                 auth_code
            )                            

        except:
            return self.format_failure( 
                "Server is currently experiencing undetermined problems. \
                Please try again later." )    
    
    
    #///////////////////////////////////////////////
    
      
    def register_request( self, request ):
        """
            Once the user has accepted an authorization request, the catalog
            must check that the resource provider is happy to permit the query 
            to be run on its server. If this fails a RegisterException will
            be thrown that the calling function must handle accordingly.
        """
        
        #build up the required data parameters for the communication
        data = urllib.urlencode( {
                'client_id': request[ "client_id" ],
                'shared_secret': request[ "shared_secret" ],
                'resource_id': request[ "resource_id" ],
                'query': request[ "query" ],
                'expiry_time': request[ "expiry_time" ],
            }
        )

        url = "%s/register_request" % ( request[ "resource_uri" ], )

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
        except urllib2.URLError, e:
            raise RegistrationException( "Failure - could not contact resource provider (%s)" % e )
        
        #parse the json response from the provider
        try:
            output = json.loads( 
                output.replace( '\r\n','\n' ), 
                strict=False 
            )

        except:
            raise RegistrationException( "Invalid json returned by the resource provider" )

        #determine whether the request has been successfully
        #registered on the resource provider
        try:
            success = output[ "success" ]
        except:
            #if we don't get a response then the agreed schema has
            #not been fulfilled by the resource provider. Bail.
            raise RegistrationException( "Resource provider has not returned successfully - unknown error" )

        #if it has then extract the access_token that will be used
        if success:
            try:
                access_token = output[ "return" ][ "access_token" ]
                return access_token
            except:
                #something has gone seriously wrong with the resource provider's
                #handling of the communication as it should have returned a key
                cause = "Resouce provider failed to supply access token" 
        else: 
            try:
                #if there is a problem we should have been sent a cause
                cause = "%s: %s" % ( output[ "error" ], output[ "error_description" ], )
            except:
                #if not simply report that we don't know what has gone awry
                cause = "Unknown problems accepting request."
        
        #if we have reached here something has gone wrong - report it        
        raise RegistrationException( cause )
        

    #///////////////////////////////////////////////
    
        
    def access( self, grant_type, redirect_uri, auth_code ):
        
        try:
           
            if grant_type != "authorization_code" :
                return self.format_access_failure(
                    "unsupported_grant_type",
                    "Grant type is either missing or incorrect"
                )  
                                
            #check that the client_id exists and is valid
            if ( redirect_uri is None or auth_code is None ) :
                return self.format_access_failure(
                    "invalid_request",
                    "A valid redirect_uri and authorization code must be provided"
                )  
            
            #so far so good. Add the request to the user's database
            #Note that if the resource the client has requested access to
            #doesn't exist, the database will throw a foreign key error.
            try:
                request = self.db.fetch_request_by_auth_code( auth_code )
                
                if request == None :
                    return self.format_access_failure(
                        "invalid_grant", 
                        "Authorization Code supplied is unrecognized" 
                    )  
                    
                if not request[ "redirect_uri" ] == redirect_uri :
                    return self.format_access_failure(
                        "invalid_client", 
                        "Client redirect_uri is incorrect for that code" 
                    )  
                
                if not request[ "access_token" ]  :
                    return self.format_access_failure(
                        "server_error", 
                        "No access token seems to be available for that code" 
                    )
                    
                return self.format_access_success( request[ "access_token" ] ) 
            
            #determine if there has been a database error
            except MySQLdb.Error:
                return self.format_access_failure(
                    "server_error", 
                    "Database problems are currently being experienced" 
                ) 

        #determine if there has been a database error
        except Exception:
            return self.format_access_failure(
                "server_error", 
                "An unknown error has occurred" 
            )             

                 
    #///////////////////////////////////////////////
    
    
    def reject_request( self, user_id, request_id ):
        
        try:   
            #check that the user_id exists and is valid
            user = self.db.fetch_user_by_id( user_id )
    
            if not ( user ) :
                return self.format_failure( 
                    "A valid user ID and has not been provided." )
            
            if not ( request_id ) :        
                return self.format_failure( 
                    "A valid request ID and has not been provided." )
                    
            #check that the request_id exists and is pending
            access_request = self.db.fetch_request_by_id( request_id )
            
            if not ( access_request ) :
                return self.format_failure( 
                    "The request you are trying to reject does not exist." ) 
            
            if not ( access_request[ "user_id" ] == user_id ) :
                return self.format_failure( 
                    "Incorrect user authentication for that request." ) 
            
            if ( not access_request[ "request_status" ] == Status.PENDING ):
                return self.format_failure( 
                    "This request has already been authorized." )   
    
            result = self.db.delete_request( request_id )

            if ( not result ):
                return self.format_failure( 
                    "Server is currently experiencing database problems. Please try again later." )     

            self.db.commit()
            
            #the request has been revoked so build the redirect url that will
            #notify the client via the user's browser
            return self.format_revoke_success( 
                access_request[ "redirect_uri" ],
                access_request[ "state" ],
                "The user denied your request."
            )
            
        except:
            return self.format_failure( 
                "Server is currently experiencing undetermined problems. Please try again later." )            
                
    
    #///////////////////////////////////////////////
    
    
    def revoke_request( self, user_id, request_id ):
        
        try:   
            #check that the user_id exists and is valid
            user = self.db.fetch_user_by_id( user_id )

            if not ( user ) :        
                return self.format_failure( 
                    "A valid user ID and has not been provided." )
                
            if not ( request_id ) :
                return self.format_failure( 
                    "A valid request ID and has not been provided." )        
                    
            #check that the request_id exists and is pending
            access_request = self.db.fetch_request_by_id( request_id )

            if not ( access_request ) :        
                return self.format_failure( 
                    "The processing request that you are trying to revoke does not exist." ) 
            
            if not ( access_request[ "user_id" ] == user_id ) :        
                return self.format_failure( 
                    "Incorrect user authentication for that request." ) 
                         
            if ( not access_request[ "request_status" ] == Status.ACCEPTED ):
                return self.format_failure( 
                    "This processing request has not been authorized, and so cannot be revoked." )   
           
            # contact the resource provider and tell them we have cancelled the
            # request so they should delete it, and its access_token from their records
            try:     
                self.deregister_request( access_request )
            except DeregisterException, e:
                return self.format_failure(
                    "Abandoned revoke - problem at Resource Provider: \"%s\"." % ( e.msg, ),
                    "resource_provider" )      
            except:
                return self.format_failure( 
                    "Abandoned revoke - undetermined problem at Resource Provider", 
                    "resource_provider" )
     
            result = self.db.delete_request( request_id )
            
            if ( not result ):
                return self.format_failure( 
                    "Server is currently experiencing database problems. Please try again later." )     

            self.db.commit()

            return self.format_revoke_success( 
                access_request[ "redirect_uri" ],
                access_request[ "state" ],
                "The user denied your request."
            )

        except:

            return self.format_failure( 
                "Server is currently experiencing problems. \
                Please try again later." )            
        

    #///////////////////////////////////////////////
    
    
    def deregister_request( self, request ):
        
        """
            Once the user has revoked an authorization request, the catalog
            must tell the resource provider to deregister that query 
        """
        
        #build up the required data parameters for the communication
        data = urllib.urlencode( {
                'access_token': request[ "access_token" ],
                'shared_secret': request[ "shared_secret" ],
            }
        )
        
        url = "%s/deregister_request" % ( request[ "resource_uri" ], )
        
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
            raise DeregisterException( "Resource provider uncontactable. Please Try again later." )

        #parse the json response from the provider
        try:
            output = json.loads( 
                output.replace( '\r\n','\n' ), 
                strict=False 
            )

        except:
            raise DeregisterException( "Invalid json returned by the resource provider" )

        #determine whether the request has been successfully
        #deregistered on the resource provider
        try:
            success = output[ "success" ]
        except:
            #if we don't get a response then the agreed schema has
            #not been fulfilled by the resource provider. Bail.
            raise DeregisterException( "Resource provider has not returned successfully - unknown error" )

        #if it has then extract the access_token that will be used
        if not success:
            try:
                #if there is a problem we should have been sent a cause
                cause = output[ "error" ][ "message" ]
            except:
                #if not simply report that we don't know what has gone awry
                cause = "reason unknown"
            
            raise DeregisterException( cause )
    

    #///////////////////////////////////////////////
        
             
    def generateAuthorizationCode( self ):
        
        token = base64.b64encode(  
            hashlib.sha256( 
                str( random.getrandbits( 256 ) ) 
            ).digest() 
        )  
            
        #replace plus signs with asterisks. Plus signs are reserved
        #characters in ajax transmissions, so just cause problems
        return token.replace( '+', '*' ) 

