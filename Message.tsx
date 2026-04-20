import React from 'react';

export interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

const Message: React.FC<MessageProps> = ({ role, content, timestamp }) => {
  const isUser = role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
        isUser 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-800 text-gray-100 border border-gray-700'
      }`}>
        <div className="flex items-start gap-2">
          <div className="flex-1">
            <div className="text-xs font-semibold mb-1 opacity-70">
              {isUser ? 'You' : 'JailbrokeGPT'}
            </div>
            <div className="text-sm whitespace-pre-wrap break-words">
              {content}
            </div>
          </div>
        </div>
        {timestamp && (
          <div className="text-xs opacity-50 mt-1">
            {timestamp.toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
