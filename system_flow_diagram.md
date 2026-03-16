# Expense API - Authentication & Data Flow Architecture

This diagram illustrates how a client application interacts with the backend. It strictly visually enforces that **Authentication happens first**, and all other routes are securely protected behind the Token Validation Middleware.

```mermaid
flowchart TD
    %% Define main actors and layers
    Client_App["Client Application (Frontend / Mobile / Postman)"]

    %% Authentication Gateway Layer
    subgraph Authentication_Layer ["Authentication Gateway Layer"]
        POST_Register["POST /auth/register"]
        POST_Login["POST /auth/login"]
        Token_Middleware{"token_required (JWT Validation)"}
    end

    %% The Protected REST API Routes
    subgraph Protected_Routes ["Protected API Routes"]
        Route_Expenses["/expense (CRUD Actions)"]
        Route_Users["/users (Manage Profile)"]
        Route_Analytics["/analytics (View Spending History)"]
    end

    %% Internal Business Logic
    subgraph Service_Layer ["Business Services Layer"]
        Service_Auth["Auth & Token Service"]
        Service_User["User Service"]
        Service_Expense["Expense Service"]
    end

    %% External Data Storage Layers
    subgraph Data_Storage ["Data Storage Layer"]
        DB_Postgres[("PostgreSQL (Primary Database)")]
    end

    %% -------------------------------------
    %% Step 1 & 2: Public Login / Registration
    %% -------------------------------------
    Client_App -->|"1. User Registers Account"| POST_Register
    POST_Register -->|"Verifies unique email"| Service_User
    Service_User -->|"Saves new record"| DB_Postgres

    Client_App -->|"2. User Logs In"| POST_Login
    POST_Login -->|"Validates Password"| Service_Auth
    Service_Auth -->|"Reads user records"| DB_Postgres
    Service_Auth -->|"Returns Access & Refresh Tokens"| Client_App

    %% -------------------------------------
    %% Step 3: Accessing Protected Data
    %% -------------------------------------
    Client_App -->|"3. Client sends Authorization Header"| Token_Middleware

    %% IF Token Fails
    Token_Middleware -->|"Invalid or Expired JWT"| Blocked["🛑 401 Unauthorized (Request Blocked)"]
    
    %% IF Token Passes
    Token_Middleware -->|"Valid JWT (Authorizes Access)"| Route_Expenses
    Token_Middleware -->|"Valid JWT (Authorizes Access)"| Route_Users
    Token_Middleware -->|"Valid JWT (Authorizes Access)"| Route_Analytics

    %% -------------------------------------
    %% Step 4: Routing down to the Services
    %% -------------------------------------
    Route_Expenses -->|"Executes Business Rules"| Service_Expense
    Route_Users -->|"Executes Business Rules"| Service_User
    Route_Analytics -->|"Requests Aggregated Data"| Service_Expense
    Route_Analytics -->|"Requests Profile Settings"| Service_User

    %% -------------------------------------
    %% Step 5: Services to Data Storage
    %% -------------------------------------
    Service_Expense <-->|"CRUD Operations"| DB_Postgres

```

### Key Architectural Concepts Visualized
1. **The Auth Vault**: Nobody gets past the `Token_Middleware` without a valid, unexpired token. It acts as a strict gateway.
2. **Service Layer Isolation**: The routes (e.g., `/expense`) never interact with PostgreSQL directly. They delegate entirely to the `Service_Layer`.
3. **Caching**: Redis is used strictly at the `Service_Layer` for extremely fast retrieval of monthly budget configurations.
