//
//  TSSafariViewControllerDelegate.h
//  ExampleApp
//
//  Created by Adam Bard on 2015-09-12.
//  Copyright © 2015 Example. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "TSHelpers.h"

#if __IPHONE_OS_VERSION_MAX_ALLOWED >= 90000 && (TEST_IOS || TARGET_OS_IPHONE || TARGET_IPHONE_SIMULATOR)

#ifndef TS_SAFARI_VIEW_CONTROLLER_ENABLED
#define TS_SAFARI_VIEW_CONTROLLER_ENABLED
#endif

#import <SafariServices/SafariServices.h>
#import <UIKit/UIKit.h>

@interface TSSafariViewControllerDelegate : UIViewController<SFSafariViewControllerDelegate>

@property(nonatomic, STRONG_OR_RETAIN) NSURL* url;
@property(nonatomic, STRONG_OR_RETAIN) void (^completion)(void);
@property(nonatomic, STRONG_OR_RETAIN) UIViewController* parent;

+ (TSSafariViewControllerDelegate*)createWithURLAndCompletion:(NSURL*)url completion:(void (^)(void))completion;

@end
#else // IOS < 9
@interface TSSafariViewControllerDelegate : NSObject
+ (TSSafariViewControllerDelegate*)createWithURLAndCompletion:(NSURL*)url completion:(void (^)(void))completion;
@end
#endif
