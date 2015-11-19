//
//  TSLanderDelegateWrapper.h
//  WordOfMouth
//
//  Created by Adam Bard on 2015-11-05.
//  Copyright © 2015 Tapstream. All rights reserved.
//

#ifndef TSLanderDelegateWrapper_h
#define TSLanderDelegateWrapper_h

#import "TSHelpers.h"

@interface TSLanderDelegateWrapper : NSObject<TSLanderDelegate>
@property(nonatomic, STRONG_OR_RETAIN) id<TSPlatform> platform;
@property(nonatomic, STRONG_OR_RETAIN) id<TSLanderDelegate> delegate;
@property(nonatomic, STRONG_OR_RETAIN) UIWindow* window;
- initWithPlatformAndDelegateAndWindow:(id<TSPlatform>)platform delegate:(id<TSLanderDelegate>)delegate window:(UIWindow*)window;
@end

#endif /* TSLanderDelegateWrapper_h */
