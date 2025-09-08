# Contributing to Daily Quote Generator & Admin Dashboard

We welcome contributions to make this project better! This document outlines how to contribute effectively while maintaining high code quality and supporting both open-source and commercial use cases.

## 🎯 Types of Contributions

We encourage the following types of contributions:

- **🐛 Bug Reports**: Issues with existing functionality
- **💡 Feature Requests**: New capabilities or improvements
- **🔧 Code Contributions**: Bug fixes, new features, optimizations
- **📚 Documentation**: README updates, code comments, tutorials
- **🧪 Testing**: Unit tests, integration tests, performance tests
- **🎨 UI/UX Improvements**: Frontend enhancements, design improvements
- **🔒 Security**: Vulnerability reports and fixes
- **⚡ Performance**: Optimization and efficiency improvements

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Git** installed and configured
- **Python 3.10+** for backend development
- **Node.js 18+** and **npm** for frontend development
- **Docker** (optional) for containerized development
- Code editor with TypeScript and Python support

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/daily_quote.git
   cd daily_quote
   ```

2. **Create Development Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Backend Setup**
   ```bash
   cd admin-dashboard/api
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Frontend Setup**
   ```bash
   cd admin-dashboard
   npm install
   ```

5. **Environment Configuration**
   ```bash
   cp admin-dashboard/api/.env.example admin-dashboard/api/.env
   # Configure your environment variables
   ```

## 📋 Development Guidelines

### Code Quality Standards

#### Python (Backend)
- **Style**: Follow PEP 8 guidelines
- **Type Hints**: Use type annotations for all functions
- **Documentation**: Docstrings for all public methods
- **Testing**: Write unit tests for new functionality
- **Linting**: Use `black`, `flake8`, and `mypy`

```python
def process_quote(quote: str, language: str = "en") -> Dict[str, Any]:
    """
    Process a quote for sentiment analysis and translation.
    
    Args:
        quote: The input quote text
        language: Target language code (default: "en")
        
    Returns:
        Dictionary containing processed quote data
    """
    # Implementation here
```

#### TypeScript/React (Frontend)
- **Style**: Use Prettier for formatting
- **Types**: Strict TypeScript configuration
- **Components**: Functional components with hooks
- **Testing**: Jest and React Testing Library
- **Linting**: ESLint with React and TypeScript rules

```typescript
interface QuoteData {
  id: string;
  text: string;
  author: string;
  sentiment: number;
  language: string;
}

const QuoteCard: React.FC<{ quote: QuoteData }> = ({ quote }) => {
  // Component implementation
};
```

### Commit Message Format

Use conventional commits for clear history:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(admin): add bulk quote import functionality
fix(api): resolve authentication token expiration issue
docs(readme): update installation instructions
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update from main branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run Tests**
   ```bash
   # Backend tests
   cd admin-dashboard/api
   python -m pytest tests/

   # Frontend tests
   cd admin-dashboard
   npm test
   ```

3. **Code Quality Checks**
   ```bash
   # Python linting
   black . --check
   flake8 .
   mypy .

   # TypeScript linting
   npm run lint
   npm run type-check
   ```

### Pull Request Template

When creating a PR, include:

```markdown
## 📝 Description
Brief description of changes

## 🎯 Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## 🧪 Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## 📋 Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 📄 Licensing and Commercial Use

### Apache 2.0 License

All contributions are made under the **Apache License 2.0**, which:

- ✅ **Allows Commercial Use**: You can use this software commercially
- ✅ **Allows Modification**: You can modify and distribute changes
- ✅ **Allows Distribution**: You can distribute original or modified versions
- ✅ **Allows Patent Use**: Grants patent rights from contributors
- ✅ **Allows Private Use**: You can use privately without restrictions

### Commercial Development Guidelines

For commercial use and development:

1. **Attribution**: Maintain copyright notices and license information
2. **Patent Protection**: Apache 2.0 provides patent protection
3. **Trademark**: Respect project trademarks and branding
4. **Contributions**: Commercial improvements are encouraged to be contributed back
5. **Support**: Commercial users can purchase professional support

### Contributor License Agreement (CLA)

By contributing, you agree that:

- Your contributions are your original work or you have rights to contribute
- You grant the project maintainers perpetual rights to use your contributions
- Your contributions are made under the Apache 2.0 license
- You understand this project may be used commercially

## 🐛 Issue Reporting

### Bug Reports

Use our [issue template](https://github.com/hipnologo/daily_quote/issues/new?template=bug_report.md):

```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
Steps to reproduce the behavior

**Expected behavior**
What you expected to happen

**Environment:**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g., 3.10.5]
- Node.js version: [e.g., 18.16.0]
- Browser: [e.g., Chrome 114, Firefox 115]

**Additional context**
Screenshots, logs, or other relevant information
```

### Security Issues

For security vulnerabilities:

1. **DO NOT** create public issues
2. Email security concerns to: [security@fabiocarvalho.dev]
3. Include detailed reproduction steps
4. Allow reasonable time for response before disclosure

## 🏗️ Architecture Guidelines

### Backend (FastAPI)
- **Modular Design**: Separate concerns into distinct modules
- **Dependency Injection**: Use FastAPI's dependency system
- **Error Handling**: Consistent error responses and logging
- **API Versioning**: Version endpoints for breaking changes
- **Database**: Use SQLAlchemy ORM with proper migrations

### Frontend (React + TypeScript)
- **Component Structure**: Atomic design principles
- **State Management**: React Query for server state, Context for client state
- **Routing**: React Router with protected routes
- **Styling**: Tailwind CSS with consistent design system
- **Performance**: Code splitting and lazy loading

### Testing Strategy
- **Unit Tests**: Individual component/function testing
- **Integration Tests**: API endpoint and component integration
- **E2E Tests**: Critical user journey testing
- **Performance Tests**: Load testing for API endpoints

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be Respectful**: Treat all contributors with respect
- **Be Collaborative**: Work together towards common goals
- **Be Professional**: Maintain professional communication
- **Be Inclusive**: Welcome contributors from all backgrounds
- **Be Constructive**: Provide helpful feedback and suggestions

### Getting Help

- **Documentation**: Check README and docs/ folder first
- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Create issues for bugs and feature requests
- **Discord**: Join our community Discord server (link in README)

## 📈 Roadmap and Priorities

Current development priorities:

1. **Performance Optimization**: API response times and frontend rendering
2. **Mobile Responsiveness**: Better mobile experience
3. **Internationalization**: Multi-language UI support
4. **Advanced Analytics**: Enhanced sentiment analysis and reporting
5. **API Extensions**: Additional endpoints and functionality

## 🎉 Recognition

Contributors will be recognized through:

- **Contributors Page**: Listed in project documentation
- **Release Notes**: Mentioned in version release notes
- **Social Media**: Highlighted on project social media
- **Swag**: Stickers and merchandise for significant contributions

---

## 📞 Contact

- **Project Maintainer**: Fabio Carvalho
- **GitHub**: [@hipnologo](https://github.com/hipnologo)

Thank you for contributing to the Daily Quote Generator & Admin Dashboard! 🚀