#!/bin/bash
# Setup Code Signing Credentials

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          OmniMind Code Signing - Secure Setup                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if credentials are already in environment
if [[ -n "$OMNIMIND_AUTHOR_NAME" ]] && [[ -n "$OMNIMIND_AUTHOR_EMAIL" ]]; then
    echo -e "${GREEN}✓ Credentials found in environment${NC}"
    echo "  Author: $OMNIMIND_AUTHOR_NAME"
    echo "  Email:  $OMNIMIND_AUTHOR_EMAIL"
    if [[ -n "$OMNIMIND_AUTHOR_LATTES" ]]; then
        echo "  Lattes: $OMNIMIND_AUTHOR_LATTES"
    fi
    echo ""
    read -p "Use these credentials? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Using existing credentials${NC}"
        export USE_ENV_CREDENTIALS=1
    else
        unset OMNIMIND_AUTHOR_NAME
        unset OMNIMIND_AUTHOR_EMAIL
        unset OMNIMIND_AUTHOR_LATTES
    fi
fi

# If not using env credentials, prompt user
if [[ -z "$USE_ENV_CREDENTIALS" ]]; then
    echo -e "${YELLOW}Enter your credentials to sign code modules:${NC}"
    echo ""
    
    read -p "Full Name: " AUTHOR_NAME
    if [[ -z "$AUTHOR_NAME" ]]; then
        echo -e "${RED}✗ Name is required${NC}"
        exit 1
    fi
    
    read -p "Email: " AUTHOR_EMAIL
    if [[ -z "$AUTHOR_EMAIL" ]]; then
        echo -e "${RED}✗ Email is required${NC}"
        exit 1
    fi
    
    read -p "Lattes URL (optional, press Enter to skip): " AUTHOR_LATTES
    
    export OMNIMIND_AUTHOR_NAME="$AUTHOR_NAME"
    export OMNIMIND_AUTHOR_EMAIL="$AUTHOR_EMAIL"
    if [[ -n "$AUTHOR_LATTES" ]]; then
        export OMNIMIND_AUTHOR_LATTES="$AUTHOR_LATTES"
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Credentials configured:${NC}"
echo "  • OMNIMIND_AUTHOR_NAME=$OMNIMIND_AUTHOR_NAME"
echo "  • OMNIMIND_AUTHOR_EMAIL=$OMNIMIND_AUTHOR_EMAIL"
if [[ -n "$OMNIMIND_AUTHOR_LATTES" ]]; then
    echo "  • OMNIMIND_AUTHOR_LATTES=$OMNIMIND_AUTHOR_LATTES"
fi
echo ""
echo -e "${YELLOW}⚠️  WARNING: These credentials are stored in your shell session.${NC}"
echo "   They will be lost when you close the terminal."
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Offer to sign modules
read -p "Sign all modules in src/ now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Run in dry-run mode first? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Running in DRY-RUN mode...${NC}"
        python scripts/code_signing/sign_modules.py --dry-run
        
        echo ""
        read -p "Apply changes? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python scripts/code_signing/sign_modules.py
        fi
    else
        python scripts/code_signing/sign_modules.py
    fi
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Signing complete!${NC}"
    else
        echo ""
        echo -e "${RED}✗ Signing failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}To sign modules later, run:${NC}"
    echo ""
    echo "  python scripts/code_signing/sign_modules.py"
    echo ""
    echo -e "${YELLOW}To verify signatures:${NC}"
    echo ""
    echo "  python scripts/code_signing/sign_modules.py --verify"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
