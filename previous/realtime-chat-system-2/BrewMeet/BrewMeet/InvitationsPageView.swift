//
//  InvitationsPageView.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

struct InvitationsPageView: View {
    private let invitations = MockData.invitations
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: "cup.and.saucer.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.black)
                    Text("Coffee Invitations")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.black)
                }
                
                Spacer()
                
                if !invitations.isEmpty {
                    Badge("\(invitations.count)", color: .error)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.white)
            
            if invitations.isEmpty {
                EmptyInvitationsView()
            } else {
                ScrollView {
                    VStack(spacing: 16) {
                        ForEach(invitations) { invitation in
                            InvitationCard(invitation: invitation)
                        }
                        
                        // Tips Card
                        Card {
                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Text("💡")
                                        .font(.system(size: 16))
                                    Text("Friendly Reminder")
                                        .font(.system(size: 16, weight: .bold))
                                        .foregroundColor(.black)
                                }
                                
                                Text("We recommend chatting a bit before accepting invitations and choosing public places for safety")
                                    .font(.system(size: 14))
                                    .foregroundColor(.gray)
                                    .lineSpacing(2)
                            }
                        }
                        .background(Color.blue.opacity(0.05))
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 16)
                }
            }
        }
        .background(Color.gray.opacity(0.05))
    }
}

struct InvitationCard: View {
    let invitation: Invitation
    
    var body: some View {
        VStack(spacing: 0) {
            // User Info Header
            VStack(spacing: 12) {
                HStack(spacing: 12) {
                    AsyncImageWithFallback(
                        url: invitation.photo,
                        contentMode: .fill
                    )
                    .frame(width: 64, height: 64)
                    .clipShape(Circle())
                    
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text("\(invitation.name), \(invitation.age)")
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.black)
                            
                            Badge("Invited you", color: .secondary)
                        }
                        
                        HStack {
                            Image(systemName: "location.fill")
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                            Text(invitation.location)
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                            Text("•")
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                            Image(systemName: "clock.fill")
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                            Text(invitation.timestamp)
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                        }
                        
                        HStack(spacing: 4) {
                            ForEach(invitation.interests.prefix(3), id: \.self) { interest in
                                Badge(interest, color: .blue)
                            }
                        }
                    }
                    
                    Spacer()
                }
            }
            .padding(16)
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [Color.orange.opacity(0.1), Color.yellow.opacity(0.1)]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            
            // Message
            VStack(alignment: .leading, spacing: 8) {
                Text(invitation.message)
                    .font(.system(size: 14))
                    .foregroundColor(.black)
                    .lineSpacing(2)
            }
            .padding(16)
            .background(Color.white)
            
            // Invitation Details
            VStack(spacing: 8) {
                HStack {
                    Image(systemName: "location.fill")
                        .font(.system(size: 16))
                        .foregroundColor(.gray)
                    Text("Suggested Place: ")
                        .font(.system(size: 14))
                        .foregroundColor(.gray)
                    Text(invitation.suggestedPlace)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.black)
                    Spacer()
                }
                
                HStack {
                    Image(systemName: "clock.fill")
                        .font(.system(size: 16))
                        .foregroundColor(.gray)
                    Text("Suggested Time: ")
                        .font(.system(size: 14))
                        .foregroundColor(.gray)
                    Text(invitation.suggestedTime)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.black)
                    Spacer()
                }
                
                HStack {
                    Image(systemName: "cup.and.saucer.fill")
                        .font(.system(size: 16))
                        .foregroundColor(.gray)
                    Text("Coffee Preference: ")
                        .font(.system(size: 14))
                        .foregroundColor(.gray)
                    Text(invitation.coffeeType)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.black)
                    Spacer()
                }
            }
            .padding(16)
            .background(Color.gray.opacity(0.05))
            
            // Action Buttons
            HStack(spacing: 12) {
                CustomButton("Decline", style: .outline) {
                    handleDecline()
                }
                
                CustomButton("Chat", style: .outline) {
                    handleMessage()
                }
                
                CustomButton("Accept", style: .primary) {
                    handleAccept()
                }
            }
            .padding(16)
            .background(Color.white)
        }
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
    }
    
    private func handleDecline() {
        print("Declined invitation \(invitation.id)")
    }
    
    private func handleMessage() {
        print("Message invitation \(invitation.id)")
    }
    
    private func handleAccept() {
        print("Accepted invitation \(invitation.id)")
    }
}

struct EmptyInvitationsView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "cup.and.saucer")
                .font(.system(size: 64))
                .foregroundColor(.gray)
            
            Text("No coffee invitations yet")
                .font(.system(size: 18, weight: .medium))
                .foregroundColor(.black)
            
            Text("Coffee invitations from other users will appear here")
                .font(.system(size: 14))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .padding(32)
    }
}

#Preview {
    InvitationsPageView()
}
