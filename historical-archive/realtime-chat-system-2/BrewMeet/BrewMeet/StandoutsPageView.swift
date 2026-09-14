//
//  StandoutsPageView.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

struct StandoutsPageView: View {
    @State private var currentIndex = 0
    private let standoutUsers = MockData.standoutUsers
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: "star.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.yellow)
                    Text("Standouts")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.black)
                }
                
                Spacer()
                
                Badge("Featured", color: .warning)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.white)
            
            ScrollView {
                VStack(spacing: 16) {
                    // Info Card
                    Card {
                        HStack(spacing: 12) {
                            Image(systemName: "sparkles")
                                .font(.system(size: 20))
                                .foregroundColor(.yellow)
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Daily Featured Recommendations")
                                    .font(.system(size: 16, weight: .bold))
                                    .foregroundColor(.black)
                                
                                Text("Based on your preferences and activity, we've selected the most compatible coffee partners for you")
                                    .font(.system(size: 14))
                                    .foregroundColor(.gray)
                                    .lineSpacing(2)
                            }
                        }
                    }
                    .background(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.yellow.opacity(0.1), Color.orange.opacity(0.1)]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    
                    // Standout Cards
                    if currentIndex < standoutUsers.count {
                        ZStack(alignment: .topTrailing) {
                            ProfileCard(
                                user: standoutUsers[currentIndex],
                                onPass: handlePass,
                                onLike: handleLike
                            )
                            
                            // Standout Badge
                            Badge(standoutUsers[currentIndex].standoutReason ?? "", color: .warning)
                                .offset(x: -8, y: -8)
                        }
                    } else {
                        // No more standouts
                        Card {
                            VStack(spacing: 16) {
                        Image(systemName: "star")
                            .font(.system(size: 48))
                            .foregroundColor(.yellow)
                                
                                Text("All featured users viewed")
                                    .font(.system(size: 18, weight: .medium))
                                    .foregroundColor(.black)
                                
                                Text("New featured recommendations will be available tomorrow")
                                    .font(.system(size: 14))
                                    .foregroundColor(.gray)
                                    .multilineTextAlignment(.center)
                                
                                CustomButton("View More Recommendations", style: .outline) {
                                    // Handle action
                                }
                            }
                        }
                    }
                    
                    // Tips Card
                    Card {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("💡")
                                    .font(.system(size: 16))
                                Text("Tip")
                                    .font(.system(size: 16, weight: .bold))
                                    .foregroundColor(.black)
                            }
                            
                            Text("Standouts are high-quality matches intelligently recommended based on your coffee preferences, interests, and active times")
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
        .background(Color.gray.opacity(0.05))
    }
    
    private func handlePass() {
        if currentIndex < standoutUsers.count - 1 {
            currentIndex += 1
        }
    }
    
    private func handleLike() {
        print("Liked standout user \(standoutUsers[currentIndex].name)")
        handlePass()
    }
}

#Preview {
    StandoutsPageView()
}
