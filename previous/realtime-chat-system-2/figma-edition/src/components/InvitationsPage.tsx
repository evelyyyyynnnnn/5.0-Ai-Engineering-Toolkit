import { ImageWithFallback } from './figma/ImageWithFallback';
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Coffee, Clock, MapPin, Heart, X, MessageCircle } from "lucide-react";

interface Invitation {
  id: string;
  name: string;
  age: number;
  photo: string;
  message: string;
  timestamp: string;
  location: string;
  suggestedPlace: string;
  suggestedTime: string;
  coffeeType: string;
  interests: string[];
}

export function InvitationsPage() {
  // Mock invitation data
  const invitations: Invitation[] = [
    {
      id: "inv1",
      name: "Luna",
      age: 27,
      photo: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      message: "你好！看到你也喜欢手冲咖啡，想约你一起喝咖啡聊聊咖啡文化～",
      timestamp: "2小时前",
      location: "朝阳区",
      suggestedPlace: "蓝瓶咖啡 三里屯店",
      suggestedTime: "明天下午 3:00",
      coffeeType: "手冲咖啡",
      interests: ["咖啡", "摄影", "旅行"]
    },
    {
      id: "inv2",
      name: "Marcus",
      age: 31,
      photo: "https://images.unsplash.com/photo-1594362031308-a8a60a08e654?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b3VuZyUyMHByb2Zlc3Npb25hbCUyMGNvZmZlZXxlbnwxfHx8fDE3NTgzOTE2MzR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      message: "Hi！我在附近的咖啡厅工作，如果你有时间的话一起喝杯咖啡吧！",
      timestamp: "6小时前",
      location: "国贸",
      suggestedPlace: "星巴克 国贸店",
      suggestedTime: "周末上午 10:30",
      coffeeType: "拿铁",
      interests: ["商业", "科技", "音乐"]
    },
    {
      id: "inv3",
      name: "Aria",
      age: 25,
      photo: "https://images.unsplash.com/photo-1563722897-e6dac3cec340?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50JTIwY29mZmVlJTIwcmVhZGluZ3xlbnwxfHx8fDE3NTgzOTE2Mzd8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      message: "看到你的资料觉得我们有很多共同话题，想认识你并约个咖啡！",
      timestamp: "1天前",
      location: "望京",
      suggestedPlace: "% Arabica 望京SOHO",
      suggestedTime: "工作日晚上 7:00",
      coffeeType: "卡布奇诺",
      interests: ["设计", "艺术", "电影"]
    }
  ];

  const handleAccept = (invitationId: string) => {
    console.log(`Accepted invitation ${invitationId}`);
  };

  const handleDecline = (invitationId: string) => {
    console.log(`Declined invitation ${invitationId}`);
  };

  const handleMessage = (invitationId: string) => {
    console.log(`Message invitation ${invitationId}`);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Coffee className="w-6 h-6 text-primary" />
              <h1 className="text-xl">咖啡邀请</h1>
            </div>
            {invitations.length > 0 && (
              <Badge variant="destructive" className="rounded-full min-w-[1.5rem] h-6">
                {invitations.length}
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-md mx-auto">
        {invitations.length === 0 ? (
          <div className="p-8 text-center">
            <Coffee className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="mb-2">暂无咖啡邀请</h3>
            <p className="text-muted-foreground">
              当有人向你发起咖啡邀请时，会在这里显示
            </p>
          </div>
        ) : (
          <div className="p-4 space-y-4">
            {invitations.map((invitation) => (
              <Card key={invitation.id} className="p-0 overflow-hidden">
                {/* User Info Header */}
                <div className="p-4 bg-gradient-to-r from-orange-50 to-amber-50">
                  <div className="flex items-start gap-3">
                    <ImageWithFallback
                      src={invitation.photo}
                      alt={`${invitation.name}的头像`}
                      className="w-16 h-16 rounded-full object-cover"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4>{invitation.name}, {invitation.age}</h4>
                        <Badge variant="secondary" className="text-xs">
                          <Heart className="w-3 h-3 mr-1" />
                          邀请你
                        </Badge>
                      </div>
                      <div className="flex items-center text-sm text-muted-foreground mb-2">
                        <MapPin className="w-3 h-3 mr-1" />
                        <span>{invitation.location}</span>
                        <span className="mx-2">•</span>
                        <Clock className="w-3 h-3 mr-1" />
                        <span>{invitation.timestamp}</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {invitation.interests.map((interest, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {interest}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Message */}
                <div className="p-4 border-b">
                  <p className="text-sm">{invitation.message}</p>
                </div>

                {/* Invitation Details */}
                <div className="p-4 bg-muted/30 space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin className="w-4 h-4 text-muted-foreground" />
                    <span>建议地点: </span>
                    <span className="font-medium">{invitation.suggestedPlace}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    <span>建议时间: </span>
                    <span className="font-medium">{invitation.suggestedTime}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Coffee className="w-4 h-4 text-muted-foreground" />
                    <span>咖啡偏好: </span>
                    <span className="font-medium">{invitation.coffeeType}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="p-4 flex gap-3">
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => handleDecline(invitation.id)}
                  >
                    <X className="w-4 h-4 mr-2" />
                    拒绝
                  </Button>
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => handleMessage(invitation.id)}
                  >
                    <MessageCircle className="w-4 h-4 mr-2" />
                    聊天
                  </Button>
                  <Button 
                    className="flex-1 bg-orange-600 hover:bg-orange-700"
                    onClick={() => handleAccept(invitation.id)}
                  >
                    <Coffee className="w-4 h-4 mr-2" />
                    接受
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Tips */}
        {invitations.length > 0 && (
          <div className="p-4">
            <Card className="p-4 bg-blue-50 border-blue-200">
              <h4 className="mb-2 text-blue-900">💡 温馨提示</h4>
              <p className="text-sm text-blue-700">
                接受邀请前建议先聊几句，选择公共场所见面更安全
              </p>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}