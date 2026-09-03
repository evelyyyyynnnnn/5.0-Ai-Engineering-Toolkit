import { ImageWithFallback } from './figma/ImageWithFallback';
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { MessageCircle, Coffee, MapPin } from "lucide-react";

interface Chat {
  id: string;
  name: string;
  photo: string;
  lastMessage: string;
  timestamp: string;
  unread: boolean;
  matched: boolean;
  location: string;
  status: 'matched' | 'planning' | 'scheduled' | 'completed';
}

interface ChatListProps {
  onChatClick: (chatId: string) => void;
}

export function ChatList({ onChatClick }: ChatListProps) {
  // Mock chat data
  const chats: Chat[] = [
    {
      id: "1",
      name: "Alice",
      photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      lastMessage: "明天下午3点在三里屯星巴克怎么样？",
      timestamp: "2小时前",
      unread: true,
      matched: true,
      location: "三里屯",
      status: "planning"
    },
    {
      id: "2", 
      name: "David",
      photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      lastMessage: "很高兴认识你！什么时候有空喝咖啡？",
      timestamp: "1天前",
      unread: false,
      matched: true,
      location: "国贸",
      status: "matched"
    },
    {
      id: "3",
      name: "Emma",
      photo: "https://images.unsplash.com/photo-1563722897-e6dac3cec340?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwY29mZmVlJTIwcmVhZGluZ3xlbnwxfHx8fDE3NTgzOTE2Mzd8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      lastMessage: "谢谢你推荐的咖啡店，改天再约！",
      timestamp: "3天前",
      unread: false,
      matched: true,
      location: "望京",
      status: "completed"
    }
  ];

  const getStatusBadge = (status: Chat['status']) => {
    switch (status) {
      case 'matched':
        return <Badge variant="secondary">新匹配</Badge>;
      case 'planning':
        return <Badge variant="default">计划中</Badge>;
      case 'scheduled':
        return <Badge className="bg-green-100 text-green-800">已约定</Badge>;
      case 'completed':
        return <Badge variant="outline">已完成</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b p-4">
        <div className="max-w-md mx-auto">
          <h1 className="text-xl">聊天</h1>
        </div>
      </div>

      <div className="max-w-md mx-auto">
        {chats.length === 0 ? (
          <div className="p-8 text-center">
            <MessageCircle className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="mb-2">还没有聊天记录</h3>
            <p className="text-muted-foreground">
              开始匹配咖啡伙伴，展开有趣的对话吧！
            </p>
          </div>
        ) : (
          <div className="divide-y">
            {chats.map((chat) => (
              <Card 
                key={chat.id}
                className="p-4 border-0 border-b rounded-none cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => onChatClick(chat.id)}
              >
                <div className="flex gap-3">
                  <div className="relative">
                    <ImageWithFallback
                      src={chat.photo}
                      alt={`${chat.name}的头像`}
                      className="w-14 h-14 rounded-full object-cover"
                    />
                    {chat.unread && (
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full" />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <h4 className="truncate">{chat.name}</h4>
                        {getStatusBadge(chat.status)}
                      </div>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {chat.timestamp}
                      </span>
                    </div>
                    
                    <div className="flex items-center text-xs text-muted-foreground mb-2">
                      <MapPin className="w-3 h-3 mr-1" />
                      <span>{chat.location}</span>
                    </div>
                    
                    <p className={`text-sm truncate ${
                      chat.unread ? 'text-foreground' : 'text-muted-foreground'
                    }`}>
                      {chat.lastMessage}
                    </p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Quick Actions */}
        <div className="p-4 space-y-3">
          <Button variant="outline" className="w-full">
            <Coffee className="w-4 h-4 mr-2" />
            发起群聊咖啡
          </Button>
        </div>
      </div>
    </div>
  );
}