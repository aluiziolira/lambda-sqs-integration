# Lambda ➜ SQS Integration

Mermaid diagram, setup instructions, metrics…

```mermaid
flowchart TD
    API[API Gateway] -->  < /dev/null | invoke| L[Lambda]
    L --> |send| Q[SQS Queue]
```
