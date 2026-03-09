import React, { type FC } from 'react';

interface CardProps {
    children: React.ReactNode;
    className?: string;
    variant?: 'default' | 'outlined' | 'elevated';
    onClick?: () => void;
}

const Card: FC<CardProps> = ({
    children,
    className = '',
    variant = 'default',
    onClick
}) => {
    const variantClasses = {
        default: 'bg-white border border-gray-200',
        outlined: 'bg-transparent border-2 border-gray-300',
        elevated: 'bg-white shadow-md border border-gray-100',
    };

    return (
        <div onClick={onClick} className={`rounded-lg ${variantClasses[variant]} ${className} `}>
            {children}
        </div>
    );
};

interface CardHeaderProps {
    children: React.ReactNode;
    className?: string;
}

const CardHeader: FC<CardHeaderProps> = ({ children, className = '' }) => {
    return (
        <div className={`px-4 py-3 border-b border-gray-200 ${className}`}>
            {children}
        </div>
    );
};

interface CardBodyProps {
    children: React.ReactNode;
    className?: string;
}

const CardBody: FC<CardBodyProps> = ({ children, className = '' }) => {
    return (
        <div className={`px-4 py-3 ${className}`}>
            {children}
        </div>
    );
};

interface CardFooterProps {
    children: React.ReactNode;
    className?: string;
}

const CardFooter: FC<CardFooterProps> = ({ children, className = '' }) => {
    return (
        <div className={`px-4 py-3 border-t border-gray-200 ${className}`}>
            {children}
        </div>
    );
};

export { Card, CardHeader, CardBody, CardFooter };