# Contributing to SignBridge AI

Thank you for contributing to SignBridge AI!

## Code Style & Standards
- **Backend**: Python 3.10+, PEP 8 formatting, type annotations on all function signatures.
- **Frontend**: React 18, functional components with hooks, TailwindCSS utility classes.
- **Architecture**: Domain service patterns, repository abstractions, zero tight-coupling between ML models and transport protocols.

## Pull Request Process
1. Fork the repository and create a feature branch (`git checkout -b feature/model-optimization`).
2. Run backend tests (`pytest backend/tests/ -v`) and verify the frontend builds cleanly (`npm run build`).
3. Commit with semantic messages (`feat: add two-hand gesture support`).
4. Submit a Pull Request with an explanation of your changes and benchmark comparisons.
