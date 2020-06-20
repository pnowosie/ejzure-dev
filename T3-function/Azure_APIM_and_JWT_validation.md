# Azure APIM and JWT validation
W scenariusz-u, gdzie frontend naszej web-aplikacji komunikuje się z backendem, postawienie OAth provider, by użytkownicy mogli się uwierzytelniać za pomocą swoich kont w popularnych serwisach jest bardzo zacną opcją.

W moim przypadku spokamy się w połowie drogi, czyli mając podpisany token JWT uwierzytelnimy się do jednej ze operacji API Management - która umożliwia dodanie cytatu. Token mogła by generować usługa komunikująca się z API lub właśnie OAth provider, jeśli komunikuje się użytkownik.

Użyjemy podpisu RSA, który jest trudniej zestawić, ale jest bezpieczniejszy i przez co częściej wykorzystywany, gdyż nie wymaga by API Management posiadał klucze prywatne. 
Przy takim podpisie APIM komunikuje się z dostawcą OpenID Connect aby pobrać (asymetryczny) klucz  publiczny. Aby nie zaciemniać rozwiązania (OpenID specyfikuje szereg endpoint-ów), ja wystawię jedynie konfigurację przekazującą kluczm dla APIM.

# Generowanie kluczy
| ssh-keygen -t rsa -b 2048 -m PEM -f jwtRS256.key<br># Don't add passphrase<br>openssl rsa -in jwtRS256.key -pubout -outform PEM -out jwtRS256.key.pub |

Podejrzyjmy nasz klucz publiczny 

Pub key

    > cat jwtRS256.key.pub
    -----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs3Ia872pFYalU66wR1lN
    yV3fabRPPqD2kskM8LDzJLWwtCjbBOgIKAzaG6+rxGGmHExGduiqmiCNlOQDBXHq
    Z2x5k9UX4USVTt/02kvpbqmEeqNhrqim7vWhrcrVUlgoObdn8Xa1LsxVDShcLbL9
    MTdCT411UG5Y48GTmaD1dcdmJD5Uu2OWFxd4ja4PwOH98Gowd5sEfF/MOrctIu00
    F6RRFIi07umZDrdG3HmavbWpOrR+diheoAK5ti6W8mAIta2qNLww91cgch2Wjr1g
    Rpp12p0bqQNLwybrrGmB95AUnlnzsnzzGUL7jek1g//ny/wl0tRSe5HU/DdXK8jr
    zwIDAQAB
    -----END PUBLIC KEY-----


# Przygotowanie konfiguracji dla klucza algorytmu RS256

Aby nie konfigurować dostawcy, który zrobiłby to za nas (np. Auth0). Wystawię minimum konfiguracji OpenID przez pliki json serwowane z Blob storage.

W tym celu tworzę konto storage-owe i kontener o nazwie `openid-connect` następnie dodaje 2 pliki

- konfiguracja: https://azuresd.blob.core.windows.net/openid-connect/cowsay/openid-config.json, który wskazuje plik klucza we właściwości `jwks-uri`
- https://azuresd.blob.core.windows.net/openid-connect/cowsay/json-web-key-set.json

Na marginesie, trochę mi zajęło aby doprosić się APIMa by łyknął mój klucz. Rozwiązuje to konwerter: https://russelldavies.github.io/jwk-creator/ (👍 Open Source)

Mając przygotowaną konfigurację, konfigurujemy polisy (in-bound) dla mojej operacji 


# Konfiguracja policy validate-jwt
    <policies>
        <inbound>
            <base />
            <set-backend-service base-url="https://t3-backend.azurewebsites.net/api/addquote" />
            <validate-jwt header-name="Authorization" failed-validation-httpcode="401" failed-validation-error-message="Unauthorized" require-expiration-time="true" require-scheme="Bearer" require-signed-tokens="true">
                <openid-config url="https://azuresd.blob.core.windows.net/openid-connect/cowsay/openid-config.json" />
    ...
            </validate-jwt>
        </inbound>
    ...
    </policies>

Nie ustawiam żadnych ról (claim-ów) wystarczy aby token był właściwie podpisany oraz nie przeterminował się (właściwość `exp`)

Jeśli jesteś ciekaw co przesyłam w środku rozkoduj sobie przykładowy token w serwise JWT.io


    eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBenVyZSBBUElNIENvd1NheSIsImlzcyI6IkNobXVyb3dpc2tvLCBBenVyZSBTRCIsImF1ZCI6InQzLWJhY2tlbmQuYXp1cmV3ZWJzaXRlcy5uZXQiLCJpYXQiOjE1OTI2NDY5OTksImV4cCI6MTU5Mjc1NDQwMH0.Wp5Jl77M30jDJWhQTGygW_gYo7gniUXG7cd1ORVqgVsWxu_I_Zi8sYEJWho2rlpwGa36SKW-06wY-RNMXUmDKUn07NZvQE3NSvk9xGJ4zeNqPwbf2bzbWpTW4ZAO2sxsCZUz7mliBt7SkO1_IbG94AbyA2U3ncFg8rBVR6vaohYra_-mVBkZfsUZnnLkhrA0gt4zqzdevbAT2RjFrk9Tvmx5IwSoPfMynLHm7JqOPO5VvuDIzDdmxpArw-ECyrSaU-zwH4hHTTG9eC3qUq1h1-gMZbV2HjXcpXA98qu7bp_gH6cWCC4FRIA-te3mCjZaOc76locjcLRzEdkUJ2dR_A

Możesz zweryfikować podpis podając również klucz publiczny 👆 

Można przetestować nasze nowe zabezpieczenia w APIM w zakładce testów.

Diagnozowanie problemów utworzenia `policy`  - lekko pomocny bywa w APIM karta “Activity Log”

Problemy z tokenem - i wszelkie inne problemy requestów do APIM ładnie można wyciągać z “Application Insights” - dlatego warto je spiąć z APIM.

🙏 Dziękuję za uwagę





